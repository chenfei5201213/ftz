import logging
from datetime import datetime, timedelta

from django.utils import timezone

from apps.ftz.models import Course, TermCourse, CourseScheduleStudent, CourseScheduleContent, Lesson, StudyMaterial, \
    UserStudyRecord
from apps.ftz.serializers import CourseScheduleContentSerializer, TermCourseDetailSerializer
from apps.mall.enum_config import StudyStatus
from apps.mall.exception import InsertTermContext, InsertTermStudent
from apps.user_center.models import ExternalUser
from utils.custom_exception import ErrorCode

logger = logging.getLogger(__name__)


class TermCourseService:
    def __init__(self, user_id, course_id, term_course_id: int = None):
        self.user_id = user_id
        self.course_id = course_id
        self.term_course_id = term_course_id
        self.user = None
        self.course = None
        self.term_course = None
        self.init()

    def init(self):
        self.user = ExternalUser.objects.get(id=self.user_id)
        self.course = Course.objects.get(id=self.course_id)
        self.get_only_term()

    def get_only_term(self):
        """
        获取期课
        """
        if self.term_course_id:
            self.term_course = TermCourse.objects.filter(id=self.term_course_id).get()
        else:
            course_schedule_student = CourseScheduleStudent.objects.filter(user=self.user, term_course__course_id=self.course_id).get()
            self.term_course = course_schedule_student.term_course
        return self.term_course

    def insert_student(self):
        """
        插入期课学员
        """
        term_course = self.get_only_term()
        if term_course:
            CourseScheduleStudent.objects.create(
                user=self.user,
                term_course=term_course,
                exp_time=term_course.course_end,
                study_status=StudyStatus.LOCKED.value[0]
            )
            return True
        raise InsertTermStudent('期课已结束，下次早点来吧', ErrorCode.TermCourseEndException.value)

    def insert_student_context(self):
        """
        插入期课学习内容
        """
        try:
            term_course = self.get_only_term()
            if term_course:
                # 假设您已经有一个方法来获取与term_course相关的课时列表
                lessons = self.get_lessons_for_term_course(term_course)
                for lesson in lessons:
                    # 获取与课时关联的卡片
                    cards = lesson.cards.all()
                    # 为每个卡片选择或创建一个学习素材
                    for card in cards:
                        # 假设每个卡片都有一个关联的学习素材
                        study_materials = card.study_materials.all()
                        for study_material in study_materials:
                            if study_material:
                                # 创建CourseScheduleContent实例
                                content = CourseScheduleContent(
                                    user=self.user,
                                    lesson_number=lesson.lesson_number,
                                    lesson=lesson,
                                    study_material=study_material,
                                    # term_course=term_course,
                                    study_status=1,
                                    open_time=term_course.course_start + timedelta(days=lesson.lesson_number - 1),
                                    term_course=term_course,
                                    card=card
                                    # 设置其他必要字段，例如open_time, finish_time, study_status等
                                )
                                # 保存实例到数据库
                                content.save()
        except Exception as e:
            logger.exception(f"插入期课内容异常")
            raise InsertTermContext("插入期课内容异常", ErrorCode.TermCourseException.value)

    def get_lessons_for_term_course(self, term_course):
        """
        获取指定期课的所有课时，并按照lesson_number升序排列
        """
        # 根据term_course来查询课时，并按照lesson_number升序排列
        lessons = Lesson.objects.filter(course_id=term_course.course).order_by('lesson_number')
        return lessons

    def get_study_material(self, lesson_number):
        """
        获取学习素材，根据课时序号排序
        """
        term_course = self.get_only_term()
        if term_course:
            study_materials = StudyMaterial.objects.filter(
                courseschedulecontent__term_course=term_course,
                courseschedulecontent__lesson_number=lesson_number
            ).order_by('courseschedulecontent__lesson_number')
            return study_materials
        return []

    def get_term_course_content(self, term_course_id=None):
        if term_course_id:
            term_course = TermCourse.objects.filter(id=term_course_id).first()
        else:
            term_course = self.get_only_term()
        if term_course:
            term_course_content = CourseScheduleContent.objects.filter(user=self.user,
                                                                       term_course=term_course).all()

            serializer = CourseScheduleContentSerializer(term_course_content, many=True)

            return serializer.data
        else:
            return []

    def insert_study_content_finish(self, study_material_id, lesson_id, status, study_duration, card_id):
        """学习过程中，上报学习状态"""
        course_content = CourseScheduleContent.objects.filter(user=self.user_id, lesson=lesson_id,
                                                              study_material=study_material_id).first()
        if not course_content:
            lesson_obj = Lesson.objects.filter(id=lesson_id).get()
            course_content = CourseScheduleContent.objects.create(
                user=self.user,
                lesson_number=lesson_obj.lesson_number,
                lesson=lesson_obj,
                term_course=self.term_course,
                study_material_id=study_material_id,
                card_id=card_id,
                # open_time=self.term_course.course_start,
                open_time=self.term_course.course_start + timedelta(days=lesson_obj.lesson_number - 1),
                study_status=status
            )
            course_content.save()
        user_study_record = UserStudyRecord(user=course_content.user, lesson_number=course_content.lesson_number,
                                            lesson=course_content.lesson,
                                            study_material=course_content.study_material,
                                            study_duration=study_duration)
        user_study_record.save()

    def update_study_status(self, study_material_id, lesson_id, status, study_duration):
        """
        更新学习状态，状态不支持回退
        """
        course_content = CourseScheduleContent.objects.filter(user=self.user_id, lesson=lesson_id,
                                                              study_material=study_material_id).first()
        if not course_content:
            # 学习的素材不存在，从同课时的素材里取第一个，重新插入相同内容，更新id
            _course_content = CourseScheduleContent.objects.filter(user=self.user_id, lesson=lesson_id).first()
            if not _course_content:
                logger.error(
                    f'同课时下没有素材，study_material_id:{study_material_id}, lesson_id={lesson_id}, user={self.user_id}')
                return
            course_content = CourseScheduleContent.objects.create(
                user=_course_content.user,
                lesson_number=_course_content.lesson_number,
                lesson=_course_content.lesson,
                term_course=_course_content.term_course,
                study_material_id=study_material_id,
                card=_course_content.card,
                open_time=_course_content.open_time,
                study_status=StudyStatus.UNLOCKED.value[0]
            )
            course_content.save()
        if course_content and course_content.study_status < status:
            course_content.study_status = status
            course_content.finish_time = timezone.now()
            course_content.save()
            user_study_record = UserStudyRecord(user=course_content.user, lesson_number=course_content.lesson_number,
                                                lesson=course_content.lesson,
                                                study_material=course_content.study_material,
                                                study_duration=study_duration)
            user_study_record.save()
        else:
            logger.info(
                f'study_material_id: {study_material_id}, lesson_id: {lesson_id} 当前状态为：{course_content}, 目标状态：{status},不允许回退状态，默认不处理')
        return course_content

