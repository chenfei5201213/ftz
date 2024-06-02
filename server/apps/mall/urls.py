from django.urls import path, include
from rest_framework import routers

from .views import ProductViewSet, OrderViewSet, PaymentRecordViewSet, OrderCreate, PaymentCreate, ProductSellViewSet, \
    MyOrderView, SellingView

router = routers.DefaultRouter()
router.register('product', ProductViewSet, basename='product')
router.register('sell', ProductSellViewSet, basename='product_sell')
router.register('order', OrderViewSet, basename='order')
router.register('pay_record', PaymentRecordViewSet, basename='pay_record')
urlpatterns = [
    path('', include(router.urls)),
    path('pay/create_order/', OrderCreate.as_view(), name='order_crate'),
    path('pay/create_payment/', PaymentCreate.as_view(), name='order_payment'),
    path('my/order/', MyOrderView.as_view(), name='my_order'),
]
