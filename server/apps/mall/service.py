import logging
from datetime import datetime
import pandas as pd

from django.db import IntegrityError
from django.db.models import Count, Prefetch
from django.utils import timezone
from rest_framework import serializers

from utils.custom_exception import ErrorCode
from .exception import OrderException, ProductException, InsertTermContext
from .models import Product, Order, PaymentRecord
from .serializers import ProductSerializer, OrderSerializer, PaymentRecordSerializer, OrderDetailSerializer, \
    ProductSellSerializer
from ..ftz.models import Lesson, CourseScheduleContent, Course, TermCourse
from ..ftz.serializers import LessonListSerializer, LessonDetailSerializer, CourseScheduleContentDetailSerializer, \
    CourseSerializer, TermCourseDetailSerializer
from ..user_center.models import ExternalUser
from .enum_config import OrderStatus, PaymentStatus, ProductStatus, PaymentMethod, UserType, StudyStatus
from ..user_center.service import TermCourseService

logger = logging.getLogger(__name__)


class ProductService:
    def get_products(self):
        # 获取所有商品信息
        products = Product.objects.all()
        # 序列化商品信息
        serializer = ProductSerializer(products, many=True)
        return serializer.data

    def create_order(self, product_id, user_id, count=1):
        # 获取商品和用户信息
        try:
            product = Product.objects.get(id=product_id)
            if product.is_deleted or product.status != ProductStatus.OnSale.value[0]:
                logger.info(f"product: {product}")
                raise ProductException("商品不存在或者已下架", ErrorCode.ProductOff.value)
            user = ExternalUser.objects.get(id=user_id)
            total_amount = product.price * count
            # todo 添加期课学员；然后在支付成功入口生成期课内容表
            # 创建订单
            order = Order.objects.create(user=user, product=product, total_amount=total_amount,
                                         status=OrderStatus.PENDING.value)
            serializer = OrderSerializer(order)
            term_service = TermCourseService(user.id, product.course.id)
            term_service.insert_student_context()

            return serializer.data
        except Order.DoesNotExist:
            logger.error(f"订单不存在", ErrorCode.OrderNotExit.value)
            raise OrderException("订单不存在")
        except Product.DoesNotExist:
            raise ProductException("商品不存在", ErrorCode.ProductNotExit.value)
        except IntegrityError:
            raise OrderException('订单已存在，请无重复创建', ErrorCode.OrderDuplication.value)
        except InsertTermContext:
            return serializer.data
        except Exception as e:
            logger.exception(f'创建订单异常')
            raise e

    def create_payment_record(self, order_id, amount, payment_method=PaymentMethod.WECHAT.value):
        try:
            # 获取订单信息
            order = Order.objects.get(id=order_id)
            # 创建支付记录
            payment_record = PaymentRecord.objects.create(order=order, payment_method=payment_method, amount=amount,
                                                          status=PaymentStatus.PENDING.value)
            # 返回支付记录信息
            serializer = PaymentRecordSerializer(payment_record)
            # todo 调用 公众号下单
            return serializer.data
        except Order.DoesNotExist:
            raise OrderException('订单不存在', ErrorCode.OrderNotExit.value)
        except Exception as e:
            logger.exception('创建支付记录异常')
            raise e


class OrderService:
    def get_order(self, order_id):
        # 获取订单信息
        order = Order.objects.get(id=order_id)
        # 返回订单信息
        serializer = OrderSerializer(order)
        return serializer.data

    def update_order_status(self, order_id, status):
        # 获取订单信息
        order = Order.objects.get(id=order_id)
        # 更新订单状态
        order.status = status
        order.save()


class PaymentService:
    def get_payment_records(self):
        # 获取所有支付记录信息
        payment_records = PaymentRecord.objects.all()
        # 序列化支付记录信息
        serializer = PaymentRecordSerializer(payment_records, many=True)
        return serializer.data

    def create_payment_record(self, order_id, payment_method, amount):
        # 获取订单信息
        order = Order.objects.get(id=order_id)
        # 创建支付记录
        payment_record = PaymentRecord.objects.create(order=order, payment_method=payment_method, amount=amount)
        # 返回支付记录信息
        serializer = PaymentRecordSerializer(payment_record)
        return serializer.data


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
        lesson = Lesson.objects.filter(id=lesson_id).first()
        serializer = LessonDetailSerializer(lesson)
        study_content = CourseScheduleContent.objects.filter(lesson=lesson_id).first()
        lesson_info = serializer.data
        study_card_count = 0
        total_card_count = len(lesson_info.get("cards", []))
        for card in lesson_info.get("cards", []):
            _result = self.study_material_list(course_id, card.get('id'))
            total_count = _result.get("total_count")
            finish_count = _result.get("finish_count")
            card.update({
                "total_count": total_count,
                "finish_count": finish_count,
                "current_index": _result.get("current_index"),
                "next_index": _result.get("next_index"),
            })
            if finish_count == total_count:
                study_card_count += 1
        cards = lesson_info.get("cards", [{}])
        current_index = cards[study_card_count - 1]['id'] if study_card_count != 0 else cards[0]['id'],
        if type(current_index) == tuple:
            current_index = current_index[0]
        lesson_info.update({
            "open_time": study_content.open_time if study_content else None,
            "study_status": self.check_study_status(study_content),
            "total_count": total_card_count,
            "finish_count": study_card_count,
            "current_index": current_index,
            "next_index": lesson_info.get("cards", [])[study_card_count].get(
                'id') if study_card_count != 0 else current_index
        })
        return lesson_info

    def study_material_list(self, course_id, card_id):
        self.check_order_paid(course_id)
        contents = CourseScheduleContent.objects.filter(card=card_id, user=self.user_id).all()
        if not contents:
            return {}
        serializer = CourseScheduleContentDetailSerializer(contents, many=True)
        df = pd.DataFrame([item.__dict__ for item in contents])
        finish_df = df[df['study_status'] > StudyStatus.IN_PROGRESS.value[0]]
        # 筛选study_status为1的记录
        current_df = df[df['study_status'] == StudyStatus.IN_PROGRESS.value[0]]
        # status_2_records = current_df.reset_index(drop=True)

        # 获取第一条记录
        if current_df.empty:
            current_index = contents[0].study_material_id
            next_index = current_index
        else:
            first_record = current_df.iloc[0]
            current_index = first_record['study_material_id']
            next_records = df[df['study_status'] < StudyStatus.IN_PROGRESS.value[0]]
            if next_records.empty:
                next_index = 0
            else:
                next_index = next_records.iloc[0]['study_material_id']
        content_info = {}
        content_info.update({
            'total_count': len(contents),
            'finish_count': len(finish_df),
            'current_index': current_index,
            'next_index': next_index,
            'data': serializer.data
        })
        return content_info

    def check_study_status(self, study_content: CourseScheduleContent):
        if study_content:
            if study_content.open_time == StudyStatus.LOCKED.value[0] and datetime.now() >= study_content.open_time:
                return StudyStatus.UNLOCKED.value[0]
        else:
            return StudyStatus.LOCKED.value[0]
        return study_content.study_status
