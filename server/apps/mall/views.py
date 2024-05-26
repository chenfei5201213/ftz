from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from utils.custom_exception import FtzException
from .models import Product, Order, PaymentRecord
from .serializers import ProductSerializer, PaymentRecordSerializer, OrderSerializer
from .service import ProductService


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
