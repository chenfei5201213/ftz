import json
import logging

from django.db import transaction, IntegrityError
from django.db.transaction import TransactionManagementError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from utils.custom_exception import FtzException
from .enum_config import PaymentStatus
from .models import Product, Order, PaymentRecord
from .serializers import ProductSerializer, PaymentRecordSerializer, OrderSerializer, ProductSellSerializer
from .service import ProductService
from ..ftz.service import TermCourseService

from ..payments.services.wechat_pay import WeChatPayService
from ..system.authentication import ExternalUserAuth
from ..system.permission import ExternalUserPermission
from ..system.tasks import send_bug_course_success_message
from ..user_center.service import StudyContentService

logger = logging.getLogger(__name__)


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
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    # permission_classes = [AllowAny]
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Product.objects.filter().all()
    serializer_class = ProductSellSerializer
    search_fields = ['name']
    ordering_fields = ['pk']
    ordering = ['-id']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['course', 'status', 'type']

    def get_queryset(self):
        # 获取基础的查询集
        queryset = super().get_queryset().filter(term_course__enrollment_end__gte=timezone.now())

        # 获取请求中的参数
        type_param = self.request.query_params.get('type')
        status_param = self.request.query_params.get('status')

        # 根据参数过滤商品
        if type_param:
            queryset = queryset.filter(type=type_param)
        if status_param:
            queryset = queryset.filter(status=status_param)
        queryset = queryset.order_by('-id')
        return queryset

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     _data = self.get_serializer(queryset, many=True).data
    #     data = [i for i in _data if i.get('term_courses')]
    #     return Response(data)


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
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    serializer_class = OrderSerializer
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            product_service = ProductService()
            order = product_service.create_order(product_id=request.data['product'], user_id=user_id)
            return Response(order, status=status.HTTP_201_CREATED)
        except FtzException as e:
            # 捕获 IntegrityError 并返回错误响应
            data = {
                'error': e.message
            }
            data.update(**e.data)
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            # 捕获 IntegrityError 并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TransactionManagementError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'创建订单未知异常: ')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PayPayment(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    # serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            product_service = ProductService()
            order_id = request.data['order_id']
            amount = request.data['amount']
            payment_method = request.data['payment_method']
            payment_record = product_service.create_payment_record(user, order_id=order_id,
                                                                   amount=amount, payment_method=payment_method)
            return Response(payment_record)
        except FtzException as e:
            return Response(data=e.__dict__, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')
        order = Order.objects.filter(id=order_id).first()
        product_obj = order.product
        product_info = ProductSellSerializer(product_obj).data
        if order.status != PaymentStatus.PAID.value:
            wx_pay_service = WeChatPayService()
            out_trade_no = order.order_uuid
            result = wx_pay_service.query_order(out_trade_no)
            wx_code, wx_result = result
            if wx_code == 200:
                wx_result = json.loads(wx_result)
                if wx_result.get('trade_state') in ['SUCCESS', 'CLOSED']:
                    payment_record = PaymentRecord.objects.filter(order=order_id).order_by('-id').first()
                    payment_record.status = PaymentStatus[wx_result.get('trade_state')].value
                    payment_record.pay_time = wx_result.get('success_time')
                    pay_result_detail = json.loads(
                        payment_record.pay_result_detail) if payment_record.pay_result_detail else {}
                    pay_result_detail.update({'pay_success_result': wx_result})
                    payment_record.pay_result_detail = json.dumps(pay_result_detail)
                    payment_record.save()
                    order.status = PaymentStatus[wx_result.get('trade_state')].value
                    order.save()
                    send_bug_course_success_message.delay(payment_record.order.id)
        order_info = OrderSerializer(order).data

        order_info['course_info'] = product_info.get('course_info')
        order_info['term_courses'] = product_info.get('term_courses')
        return Response(order_info)


class MyOrderView(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    # serializer_class = OrderSerializer
    """
    我的订单
    """

    def get(self, request, *args, **kwargs):
        """
        参数用户名
        """
        try:
            user_id = request.user.id
            study_service = StudyContentService(user_id)
            data = study_service.my_order()
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WxPayNotify(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info(f'request.headers: {request.headers}, request.data:{request.data}')
        wx_pay_service = WeChatPayService()
        _result = wx_pay_service.callback(request.headers, request.data)
        logger.info(f'_result:{_result}')
        # _result = {'code': 'SUCCESS', 'data': {'resource':{'transaction_id': 'wx07154418608943b9047bfe2a04a8a60000'}}}
        if _result.get('code') == 'SUCCESS':
            result = _result['data']['resource']
            transaction_id = result.get('transaction_id')
            pay_record = PaymentRecord.objects.filter(pay_id=transaction_id).first()
            if pay_record.status != PaymentStatus.PAID.value:
                pay_record.status = PaymentStatus.PAID.value
                pay_record.order.status = PaymentStatus.PAID.value
                pay_record.save()
                send_bug_course_success_message.delay(pay_record.order.id)
            # 更新支付记录和订单状态
            return Response({'code': 'SUCCESS', 'message': '成功'})
        return Response({'code': 'FAILED', 'message': '失败'})
