import json

from django.utils import timezone
from rest_framework import serializers

from .models import Product, Order, PaymentRecord
from apps.ftz.serializers import CourseSerializer, TermCourseSerializer
from ..ftz.models import TermCourse


class ProductSerializer(serializers.ModelSerializer):
    """
    商品序列化
    """
    type_description = serializers.SerializerMethodField()
    status_description = serializers.SerializerMethodField()
    course_info = CourseSerializer(source='course', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_type_description(self, obj):
        return obj.type_description

    def get_status_description(self, obj):
        return obj.status_description


class ProductSellSerializer(serializers.ModelSerializer):
    """
    商品序列化
    """
    type_description = serializers.SerializerMethodField()
    status_description = serializers.SerializerMethodField()
    course_info = CourseSerializer(source='course', read_only=True)
    term_courses = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_type_description(self, obj):
        return obj.type_description

    def get_status_description(self, obj):
        return obj.status_description

    def get_term_courses(self, obj):
        # 获取与商品关联的期课信息
        # term_courses = obj.course.termcourse_set.all()
        term_courses = TermCourse.objects.filter(course=obj.course, enrollment_end__gte=timezone.now()).first()
        if not term_courses:
            return {}
        serializer = TermCourseSerializer(term_courses)
        return serializer.data


class OrderSerializer(serializers.ModelSerializer):
    """
    订单序列化
    """
    status_description = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_status_description(self, obj):
        return obj.status_description


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    订单序列化
    """
    status_description = serializers.SerializerMethodField()
    product_info = ProductSerializer(source='product')

    class Meta:
        model = Order
        fields = '__all__'

    def get_status_description(self, obj):
        return obj.status_description


class PaymentRecordSerializer(serializers.ModelSerializer):
    """
    支付记录列化
    """
    payment_method_description = serializers.SerializerMethodField()
    status_description = serializers.SerializerMethodField()
    pay_result_detail = serializers.SerializerMethodField()

    class Meta:
        model = PaymentRecord
        fields = '__all__'

    def get_payment_method_description(self, obj):
        return obj.payment_method_description

    def get_status_description(self, obj):
        return obj.status_description

    def get_pay_result_detail(self, obj):
        return json.loads(obj.pay_result_detail or '{}')
