# payments/views.py
from rest_framework import views, status
from rest_framework.response import Response
from .services.wechat_pay import WeChatPayService
from .services.alipay import AlipayService
from .models import Order, PaymentRecord

class PaymentView(views.APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        platform = request.data.get('platform')
        if platform == 'wechat':
            pay_service = WeChatPayService()
            result = pay_service.create_order(order)
        elif platform == 'alipay':
            pay_service = AlipayService()
            result = pay_service.create_order(order)
        else:
            return Response({'error': 'Invalid payment platform'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存支付记录
        PaymentRecord.objects.create(
            order=order,
            platform=platform,
            transaction_id=result['transaction_id'],
            status=result['status']
        )

        return Response(result, status=status.HTTP_201_CREATED)