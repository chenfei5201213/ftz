from django.urls import path, include
from rest_framework import routers

from .views import ProductViewSet, OrderViewSet, PaymentRecordViewSet, OrderCreate, PaymentCreate, ProductSellViewSet, \
    MyCourseView, MyOrderView, CourseLessonListView, CourseLessonDetailView, StudyMaterialView

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
    path('my/course/', MyCourseView.as_view(), name='my_course'),
    path('my/course/lesson/', CourseLessonListView.as_view(), name='my_course_lesson'),
    path('my/course/lesson/detail/', CourseLessonDetailView.as_view(), name='my_course_lesson_detail'),
    path('my/course/lesson/material/', StudyMaterialView.as_view(), name='my_course_lesson_material'),
]
