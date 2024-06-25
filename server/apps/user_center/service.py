import logging
from django.db import IntegrityError

from apps.ftz.models import TermCourse, CourseScheduleStudent, CourseScheduleContent, UserStudyRecord, StudyMaterial, \
    Course, Lesson, Card
from datetime import datetime
import pytz

from apps.ftz.serializers import CourseScheduleContentSerializer, CourseScheduleContentDetailSerializer, \
    LessonDetailSerializer, LessonListSerializer, CourseSerializer, LessonDetailSimpleListSerializer, \
    CardDetailSimpleSerializer
from apps.mall.enum_config import StudyStatus, UserType, OrderStatus, ProductType, PaymentMethod
from apps.mall.exception import InsertTermContext, OrderException
from apps.mall.models import Order, Product
from apps.mall.serializers import OrderDetailSerializer
from apps.mall.service import ProductService
from apps.user_center.models import ExternalUser
from utils.custom_exception import ErrorCode

logger = logging.getLogger(__name__)

class ExternalUserService:
    def __init__(self, unionid):
        self.unionid = unionid
        self.user_info = {}

    def save(self, user_info):
        try:
            data = {
                'openid': user_info.get('openid'),
                'mini_openid': user_info.get('mini_openid'),
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
            study_service = StudyContentService(external_user.id)
            study_service.receive_free_product(is_auto=True)
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
        courses = Course.objects.filter(id__in=course_ids).order_by('-id').all()
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
            study_content = CourseScheduleContent.objects.filter(user=self.user_id, lesson=lesson_info['id']).order_by(
                '-id').first()
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
                if not contents_dict.get(study_material):
                    logger.error(f"study_material: {study_material} 不存在")
                    continue
                if contents_dict.get(study_material)['study_status'] > StudyStatus.IN_PROGRESS.value[0]:
                    study_progress['finish_count'] += 1
            study_progress['current_index'] = card['study_materials'][max(study_progress['finish_count'] - 1, 0)]

            if study_progress['total_count'] != study_progress['finish_count']:
                study_progress['next_index'] = \
                    card['study_materials'][min(study_progress['finish_count'], study_progress['total_count'] - 1)]

            # 处理单个卡片学习完成后，一直停留在最后一个素材问题，最后一个学完后，再进入从第一个学习
            if study_progress.get('finish_count') == study_progress.get('total_count'):
                study_progress['current_index'] = card['study_materials'][0]
                study_progress['next_index'] = card['study_materials'][0]
            card['study_progress'] = study_progress

            if study_progress['total_count'] == study_progress['finish_count']:
                card['study_status'] = StudyStatus.COMPLETED.value[0]
                lesson_study_progress['finish_count'] += 1
            elif study_progress['finish_count'] > 0:
                card['study_status'] = StudyStatus.IN_PROGRESS.value[0]
            else:
                card['study_status'] = StudyStatus.UNLOCKED.value[0]

        lesson_study_progress['current_index'] = lesson['cards'][max(lesson_study_progress['finish_count'] - 1, 0)][
            'id']

        if lesson_study_progress['total_count'] != lesson_study_progress['finish_count']:
            lesson_study_progress['next_index'] = \
                lesson['cards'][min(lesson_study_progress['finish_count'], study_progress['total_count'] - 1)]['id']
        card['study_progress'] = study_progress
        if lesson_study_progress['total_count'] == lesson_study_progress['finish_count']:
            lesson['study_status'] = StudyStatus.COMPLETED.value[0]
        elif lesson_study_progress['finish_count'] > 0:
            lesson['study_status'] = StudyStatus.IN_PROGRESS.value[0]
        else:
            lesson['study_status'] = StudyStatus.UNLOCKED.value[0]

        return lesson

    def card_study_progress(self, card_obj: Card, lesson: Lesson, study_material_id=None):
        card = CardDetailSimpleSerializer(card_obj).data
        study_content = CourseScheduleContent.objects.filter(card=card_obj.id, user=self.user_id,
                                                             lesson=lesson.id).all()
        contents = CourseScheduleContentSerializer(study_content, many=True).data
        contents_dict = {i['study_material']: i for i in contents}
        study_progress = {
            "total_count": len(card['study_materials']),
            "finish_count": 0,
            "current_index": 0,
            "next_index": 0,
        }
        study_material_ids = []
        study_materials_dict = {}
        card['study_progress'] = study_progress
        for study_material in card['study_materials']:
            study_material_ids.append(study_material['id'])
            study_materials_dict[study_material['id']] = study_material
            if contents_dict.get(study_material['id'])['study_status'] > StudyStatus.IN_PROGRESS.value[0]:
                study_progress['finish_count'] += 1
        card['study_progress'] = study_progress
        if study_progress['total_count'] == study_progress['finish_count']:
            card['study_status'] = StudyStatus.COMPLETED.value[0]
        elif study_progress['finish_count'] > 0:
            card['study_status'] = StudyStatus.IN_PROGRESS.value[0]
        else:
            card['study_status'] = StudyStatus.UNLOCKED.value[0]
        card.pop('study_materials')
        study_progress['current_index'] = study_materials_dict.get(study_material_id)
        study_material_id_index = study_material_ids.index(study_material_id)
        next_index = study_material_ids[min(study_material_id_index + 1, len(study_material_ids) - 1)]
        study_progress['next_index'] = study_materials_dict.get(next_index)
        return card

    def check_study_status(self, study_content: CourseScheduleContent):
        if study_content:
            if study_content.study_status == StudyStatus.LOCKED.value[0] and datetime.now(
                    pytz.utc) >= study_content.open_time:
                return StudyStatus.UNLOCKED.value[0]
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
                study_progress['current_index'] = card['study_materials'][max(study_progress['finish_count'] - 1, 0)][
                    'id']

                if study_progress['total_count'] != study_progress['finish_count']:
                    study_progress['next_index'] = \
                        card['study_materials'][min(study_progress['finish_count'], study_progress['total_count'] - 1)][
                            'id']
                card['study_progress'] = study_progress
                if study_progress['total_count'] == study_progress['finish_count']:
                    card['study_status'] = StudyStatus.COMPLETED.value[0]
                    lesson_study_progress['finish_count'] += 1
                elif study_progress['finish_count'] > 0:
                    card['study_status'] = StudyStatus.IN_PROGRESS.value[0]
                else:
                    card['study_status'] = StudyStatus.UNLOCKED.value[0]
            lesson_study_progress['current_index'] = lesson['cards'][max(lesson_study_progress['finish_count'] - 1, 0)][
                'id']

            if lesson_study_progress['total_count'] != lesson_study_progress['finish_count']:
                lesson_study_progress['next_index'] = \
                    lesson['cards'][min(lesson_study_progress['finish_count'], study_progress['total_count'] - 1)]['id']
            card['study_progress'] = study_progress
            if lesson_study_progress['total_count'] == lesson_study_progress['finish_count']:
                lesson['study_status'] = StudyStatus.COMPLETED.value[0]
            elif lesson_study_progress['finish_count'] > 0:
                lesson['study_status'] = StudyStatus.IN_PROGRESS.value[0]
            else:
                lesson['study_status'] = StudyStatus.UNLOCKED.value[0]

        return {i['id']: i for i in lessons}

    def receive_free_product(self, free_product_id=None, is_auto=False):
        try:
            if free_product_id:
                product = Product.objects.filter(id=free_product_id).order_by('-id').first()
                if product.type != ProductType.FREE.value[0]:
                    raise OrderException("这个课程需要购买哦", ErrorCode.ProductNotFree.value)
            else:
                product = Product.objects.filter(type=ProductType.FREE.value[0]).first()
            product_service = ProductService()
            order = product_service.create_order(product.id, self.user_id)
            user = ExternalUser.objects.get(id=self.user_id)
            product_service.create_payment_record(user, order_id=order['id'], amount=order['total_amount'],
                                                  payment_method=PaymentMethod.FREE.value)
            return order
        except Exception as e:
            logger.exception(f"领取免费课程异常")
            if not is_auto:
                raise e
