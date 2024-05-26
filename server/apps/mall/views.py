from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from .models import Product, Order, PaymentRecord
from .serializers import ProductSerializer, PaymentRecordSerializer, OrderSerializer


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
    filterset_fields = ['course']


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
