from django.db import IntegrityError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from utils.custom_exception import FtzException
from .models import Product, Order, PaymentRecord
from .serializers import ProductSerializer, PaymentRecordSerializer, OrderSerializer, ProductSellSerializer
from .service import ProductService, StudyContentService
from ..ftz.models import TermCourse


class ProductViewSet(ModelViewSet):
    """
    商品-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = ['name']
    ordering_fields = ['-pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['course', 'status']


class ProductSellViewSet(ModelViewSet):
    """
    商品售卖-增删改查
    """
    permission_classes = [AllowAny]
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Product.objects.all()
    serializer_class = ProductSellSerializer
    search_fields = ['name']
    ordering_fields = ['-pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['course', 'status', 'type']

    def get_queryset(self):
        # 获取基础的查询集
        queryset = super().get_queryset()

        # 获取请求中的参数
        type_param = self.request.query_params.get('type')
        status_param = self.request.query_params.get('status')

        # 根据参数过滤商品
        if type_param:
            queryset = queryset.filter(type=type_param)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # # 获取当前时间
        # now = timezone.now()
        #
        # # 过滤出期课即将开始到未结束的商品
        # # 使用 Q 对象来构建复杂的查询
        # term_courses = TermCourse.objects.filter(
        #     # enrollment_start__lte=now,
        #     enrollment_end__gte=now
        # )
        # course_ids = term_courses.values_list('course_id', flat=True).distinct()
        # queryset = queryset.filter(course_id__in=course_ids)

        return queryset


class OrderViewSet(ModelViewSet):
    """
    订单-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    search_fields = ['user']
    ordering_fields = ['pk']
    ordering = ['-pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['user', 'product']


class PaymentRecordViewSet(ModelViewSet):
    """
    支付记录-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    search_fields = []
    ordering_fields = ['pk']
    ordering = ['-pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['status']


class OrderCreate(APIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            product_service = ProductService()
            order = product_service.create_order(product_id=request.data['product'], user_id=request.data['user'])
            return Response(order, status=status.HTTP_201_CREATED)
        except FtzException as e:
            # 捕获 IntegrityError 并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCreate(APIView):
    permission_classes = [AllowAny]
    # serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        try:
            product_service = ProductService()
            payment_record = product_service.create_payment_record(order_id=request.data['order_id'],
                                                                   amount=request.data['amount'])
            return Response(payment_record)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyOrderView(APIView):
    permission_classes = [AllowAny]
    # serializer_class = OrderSerializer
    """
    我的订单
    """

    def get(self, request, *args, **kwargs):
        """
        参数用户名
        """
        try:
            user_id = request.query_params.get('user_id')
            study_service = StudyContentService(user_id)
            data = study_service.my_order()
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellingView(APIView):
    permission_classes = [AllowAny]
    # serializer_class = OrderSerializer
    """
    售卖中的商品
    """

    def get(self, request, *args, **kwargs):
        """
        参数用户名
        """
        try:
            user_id = request.query_params.get('user_id')
            product_service = ProductService()
            data = product_service.selling_product()
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


