import logging
from collections import defaultdict

import pandas as pd
from django.db import IntegrityError
from django.db.models import Prefetch

from apps.ftz.models import TermCourse, CourseScheduleStudent, CourseScheduleContent, UserStudyRecord, StudyMaterial, \
    Course, Lesson, Card
from datetime import datetime, timedelta

from apps.ftz.serializers import CourseScheduleContentSerializer, CourseScheduleContentDetailSerializer, \
    LessonDetailSerializer, LessonListSerializer, CourseSerializer, LessonDetailSimpleListSerializer, \
    CardDetailSimpleSerializer
from apps.mall.enum_config import StudyStatus, UserType, OrderStatus
from apps.mall.exception import InsertTermContext
from apps.mall.models import Order
from apps.mall.serializers import OrderDetailSerializer
from apps.user_center.exception import ExternalUserCreateException
from apps.user_center.models import ExternalUser
from apps.user_center.serializers import ExternalUserSerializer
from utils.custom_exception import ErrorCode

logger = logging.getLogger(__name__)


class TermCourseService:
    def __init__(self, user_id, course_id):
        self.user_id = user_id
        self.course_id = course_id
        self.init()

    def init(self):
        self.user = ExternalUser.objects.get(id=self.user_id)
        self.course = Course.objects.get(id=self.course_id)
        pass

    def get_only_term(self):
        """
        获取最近一个正在售卖的期课
        """
        now = datetime.now()
        try:
            term_course = TermCourse.objects.filter(
                course=self.course,
                enrollment_start__lte=now,
                enrollment_end__gte=now,
            ).first()
            return term_course
        except TermCourse.DoesNotExist:
            return None

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
                study_status=StudyStatus.LOCKED.value[0]  # todo 这里最好使用枚举值
            )

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

    def update_study_status(self, study_material_id, lesson_id, status, study_duration):
        """
        更新学习状态，状态不支持回退
        """
        course_content = CourseScheduleContent.objects.filter(user=self.user_id, lesson=lesson_id,
                                                              study_material=study_material_id).first()
        if course_content and course_content.study_status < status:
            course_content.study_status = status
            course_content.save()
            user_study_record = UserStudyRecord(user=course_content.user, lesson_number=course_content.lesson_number,
                                                lesson=course_content.lesson,
                                                study_material=course_content.study_material,
                                                study_duration=study_duration)
            user_study_record.save()
        else:
            logger.info(
                f'study_material_id: {study_material_id}, lesson_id: {lesson_id} 当前状态为：{course_content.study_status}, 目标状态：{status},不允许回退状态，默认不处理')
        return course_content


class ExternalUserService:
    def __init__(self, unionid):
        self.unionid = unionid
        self.user_info = {}

    def save(self, user_info):
        try:
            data = {
                'openid': user_info.get('openid'),
                'nickname': user_info.get('nickname'),
                'unionid': user_info.get('unionid'),
                'gender': user_info.get('sex'),
                'country': user_info.get('country'),
                'province': user_info.get('province'),
                'city': user_info.get('city'),
                'avatar': user_info.get('headimgurl'),
            }
            self.user_info = user_info
            external_user = ExternalUser(**data)
            external_user.save()
            self.user = external_user
            return external_user
        except IntegrityError:
            raise ErrorCode.ExternalUserDuplication("用户已存在，请直接登录")
        except Exception as e:
            raise ErrorCode.ExternalUserException(e)

    def get_user(self):
        return ExternalUser.objects.filter(unionid=self.unionid).first()

    def check_user_is_exits(self):
        if self.get_user():
            return True
        else:
            return False


class StudyContentService:

    def __init__(self, user_id):
        self.user_id = user_id

    def check_order_paid(self, course_id):
        """这里先不做校验"""
        # product = Product.objects.filter(course=course_id).first()
        # paid_order = Order.objects.filter(product=product, status=OrderStatus.PAID.value).first()
        # if not paid_order:
        #     raise ErrorCode.OrderNotPaidException("订单未支付，请先完成订单支付再学习")

    def my_order(self,
                 # status=OrderStatus.PAID.value
                 ):
        """
        订单状态
        """
        orders = Order.objects.filter(user=self.user_id).all()
        serializer = OrderDetailSerializer(orders, many=True)
        return serializer.data

    def my_course(self, status=OrderStatus.PAID.value):
        """
        我的课程
        """
        data = {}
        course_ids = Order.objects.filter(user=self.user_id, status=status).values('product__course_id').all()
        courses = Course.objects.filter(id__in=course_ids).all()
        if courses:
            serializer = CourseSerializer(courses, many=True)
            data.update({
                'user_type': UserType.Member.value[0],
                'courses': serializer.data
            })
        else:
            course_ids = Order.objects.filter(user=self.user_id, status=OrderStatus.FREE.value).values(
                'product__course_id').all()
            courses = Course.objects.filter(id__in=course_ids).all()
            serializer = CourseSerializer(courses, many=True)
            data.update({
                'user_type': UserType.Guest.value[0],
                'courses': serializer.data
            })
        for course_info in data.get('courses'):
            total_count = CourseScheduleContent.objects.filter(term_course__course=course_info['id'],
                                                               user=self.user_id).count()
            finish_count = CourseScheduleContent.objects.filter(term_course__course=course_info['id'],
                                                                user=self.user_id,
                                                                study_status=StudyStatus.COMPLETED.value[0]).count()
            course_info.update({
                'lessons': self.course_lessons(course_info['id']),

                'total': total_count,
                'finish_count': finish_count
            })
        return data

    def course_lessons(self, course_id):
        """
        仅展示支付的订单，某个课程的课时
        """
        self.check_order_paid(course_id)
        lessons = Lesson.objects.filter(course_id=course_id).order_by('lesson_number').all()
        serializer = LessonListSerializer(lessons, many=True)
        lessons_info = serializer.data
        lessons_groups = {}
        for lesson_info in lessons_info:
            study_content = CourseScheduleContent.objects.filter(lesson=lesson_info['id']).first()

            lesson_info.update({
                "open_time": study_content.open_time if study_content else None,
                "study_status": self.check_study_status(study_content)
            })
            if not lessons_groups.get(lesson_info['group_name']):
                lessons_groups[lesson_info['group_name']] = [lesson_info]
            else:
                lessons_groups[lesson_info['group_name']].append(lesson_info)
        d = [{'group_name': k, 'lessons': v} for k, v in lessons_groups.items()]
        return d

    def lesson_detail(self, course_id, lesson_id):
        """
        展示某一个课时所有的内容，到卡片维度
        """
        self.check_order_paid(course_id)
        lesson_obj = Lesson.objects.filter(id=lesson_id).first()
        serializer = LessonDetailSerializer(lesson_obj)
        lesson = serializer.data
        study_content = CourseScheduleContent.objects.filter(lesson=lesson_id, user=self.user_id).all()
        contents = CourseScheduleContentSerializer(study_content, many=True).data
        contents_dict = {i['study_material']: i for i in contents}
        lesson_study_progress = {
            "total_count": len(lesson['cards']),
            "finish_count": 0,
            "current_index": 0,
            "next_index": 0,
        }
        lesson['study_progress'] = lesson_study_progress
        for card in lesson['cards']:
            study_progress = {
                "total_count": len(card['study_materials']),
                "finish_count": 0,
                "current_index": 0,
                "next_index": 0,
            }
            for study_material in card['study_materials']:

                if contents_dict.get(study_material)['study_status'] > StudyStatus.IN_PROGRESS.value[0]:
                    study_progress['finish_count'] += 1
            study_progress['current_index'] = card['study_materials'][study_progress['finish_count']]

            if study_progress['total_count'] != study_progress['finish_count']:
                study_progress['next_index'] = \
                card['study_materials'][min(study_progress['finish_count'] + 1, study_progress['total_count'] - 1)]
            card['study_progress'] = study_progress
            if study_progress['total_count'] == study_progress['finish_count']:
                card['study_status'] = StudyStatus.COMPLETED.value[0]
                lesson_study_progress['finish_count'] += 1
            elif study_progress['finish_count'] > 0:
                card['study_status'] = StudyStatus.IN_PROGRESS.value[0]
            else:
                card['study_status'] = StudyStatus.UNLOCKED.value[0]
        lesson_study_progress['current_index'] = lesson['cards'][lesson_study_progress['finish_count']]['id']

        if lesson_study_progress['total_count'] != lesson_study_progress['finish_count']:
            lesson_study_progress['next_index'] = \
            lesson['cards'][min(lesson_study_progress['finish_count'] + 1, study_progress['total_count'] - 1)]['id']
        card['study_progress'] = study_progress
        if lesson_study_progress['total_count'] == lesson_study_progress['finish_count']:
            lesson['study_status'] = StudyStatus.COMPLETED.value[0]
        elif lesson_study_progress['finish_count'] > 0:
            lesson['study_status'] = StudyStatus.IN_PROGRESS.value[0]
        else:
            lesson['study_status'] = StudyStatus.UNLOCKED.value[0]

        return lesson

    def card_study_progress(self, card_obj: Card):
        card = CardDetailSimpleSerializer(card_obj).data
        study_content = CourseScheduleContent.objects.filter(card=card_obj.id, user=self.user_id).all()
        contents = CourseScheduleContentSerializer(study_content, many=True).data
        contents_dict = {i['study_material']: i for i in contents}
        study_progress = {
            "total_count": len(card['study_materials']),
            "finish_count": 0,
            "current_index": 0,
            "next_index": 0,
        }
        card['study_progress'] = study_progress
        for study_material in card['study_materials']:

            if contents_dict.get(study_material['id'])['study_status'] > StudyStatus.IN_PROGRESS.value[0]:
                study_progress['finish_count'] += 1
        study_progress['current_index'] = card['study_materials'][study_progress['finish_count']]

        if study_progress['total_count'] != study_progress['finish_count']:
            study_progress['next_index'] = \
                card['study_materials'][min(study_progress['finish_count'] + 1, study_progress['total_count'] - 1)]
        card['study_progress'] = study_progress
        if study_progress['total_count'] == study_progress['finish_count']:
            card['study_status'] = StudyStatus.COMPLETED.value[0]
        elif study_progress['finish_count'] > 0:
            card['study_status'] = StudyStatus.IN_PROGRESS.value[0]
        else:
            card['study_status'] = StudyStatus.UNLOCKED.value[0]
        card.pop('study_materials')
        return card

    def check_study_status(self, study_content: CourseScheduleContent):
        if study_content:
            if study_content.open_time == StudyStatus.LOCKED.value[0] and datetime.now() >= study_content.open_time:
                return StudyStatus.UNLOCKED.value[0]
        else:
            return StudyStatus.LOCKED.value[0]
        return study_content.study_status

    def learning_progress(self, course_id):
        """
        学习进度
        """
        lessons_obj = Lesson.objects.filter(course_id=course_id).all()
        lessons = LessonDetailSimpleListSerializer(lessons_obj, many=True).data

        contents_obj = CourseScheduleContent.objects.filter(term_course__course=course_id, user=self.user_id).all()
        contents = CourseScheduleContentSerializer(contents_obj, many=True).data
        contents_dict = {i['study_material']: i for i in contents}
        for lesson in lessons:
            lesson_study_progress = {
                "total_count": len(lesson['cards']),
                "finish_count": 0,
                "current_index": 0,
                "next_index": 0,
            }
            lesson['study_progress'] = lesson_study_progress
            for card in lesson['cards']:
                study_progress = {
                    "total_count": len(card['study_materials']),
                    "finish_count": 0,
                    "current_index": 0,
                    "next_index": 0,
                }
                for study_material in card['study_materials']:

                    if contents_dict.get(study_material['id'])['study_status'] > StudyStatus.IN_PROGRESS.value[0]:
                        study_progress['finish_count'] += 1
                study_progress['current_index'] = card['study_materials'][study_progress['finish_count']]['id']

                if study_progress['total_count'] != study_progress['finish_count']:
                    study_progress['next_index'] = card['study_materials'][min(study_progress['finish_count'] + 1, study_progress['total_count']-1)]['id']
                card['study_progress'] = study_progress
                if study_progress['total_count'] == study_progress['finish_count']:
                    card['study_status'] = StudyStatus.COMPLETED.value[0]
                    lesson_study_progress['finish_count'] += 1
                elif study_progress['finish_count'] > 0:
                    card['study_status'] = StudyStatus.IN_PROGRESS.value[0]
                else:
                    card['study_status'] = StudyStatus.UNLOCKED.value[0]
            lesson_study_progress['current_index'] = lesson['cards'][lesson_study_progress['finish_count']]['id']

            if lesson_study_progress['total_count'] != lesson_study_progress['finish_count']:
                lesson_study_progress['next_index'] = lesson['cards'][min(lesson_study_progress['finish_count'] + 1, study_progress['total_count']-1)]['id']
            card['study_progress'] = study_progress
            if lesson_study_progress['total_count'] == lesson_study_progress['finish_count']:
                lesson['study_status'] = StudyStatus.COMPLETED.value[0]
            elif lesson_study_progress['finish_count'] > 0:
                lesson['study_status'] = StudyStatus.IN_PROGRESS.value[0]
            else:
                lesson['study_status'] = StudyStatus.UNLOCKED.value[0]

        return {i['id']: i for i in lessons}
        # df = pd.DataFrame([item.__dict__ for item in contents])

