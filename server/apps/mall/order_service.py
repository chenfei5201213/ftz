# encoding: utf-8
"""
@author: chenfei
@contact: chenfei@kuaishou.com
@software: PyCharm
@file: order_service.py
@time: 2024/10/19 11:35
"""
import json
import time
import logging

from datetime import datetime, timedelta

from apps.mall.enum_config import PaymentStatus, PaymentMethod
from apps.mall.models import PaymentRecord
from apps.payments.services.wechat_pay import WeChatPayService

logger = logging.getLogger(__name__)


class OrderPaymentSyncService:
    """
    订单支付同步服务
    """

    def sync(self, recent_payment_days=700, unpaid_days_threshold=3):
        """默认查询最近7天支付记录，如果支付记录超过3天未支付，则自动关闭支付"""
        payment_records = PaymentRecord.objects.filter(
            create_time__gte=datetime.now() - timedelta(days=recent_payment_days),
            payment_method__in=[PaymentMethod.WECHAT.value,
                                PaymentMethod.ALIPAY.value]).all()
        for payment_record in payment_records:
            if payment_record.status == PaymentStatus.PAID.value and payment_record.order.status == PaymentStatus.PAID.value:
                continue
            if payment_record.payment_method == PaymentMethod.WECHAT.value:
                self.query_wx_pay_result_and_sync(payment_record, unpaid_days_threshold)

            elif payment_record.payment_method == PaymentMethod.ALIPAY.value:
                self.query_alipay_result()

    def query_wx_pay_result_and_sync(self, payment_record, unpaid_days_threshold):
        wx_pay_service = WeChatPayService()
        order_uuid = payment_record.order.order_uuid
        result = wx_pay_service.query_order(order_uuid)
        wx_code, wx_result = result
        if wx_code == 200:
            wx_result = json.loads(wx_result)
            if wx_result.get('trade_state') in ['SUCCESS', 'CLOSED']:
                payment_record.status = PaymentStatus[wx_result.get('trade_state')].value
                payment_record.pay_time = wx_result.get('success_time')
                pay_result_detail = json.loads(
                    payment_record.pay_result_detail) if payment_record.pay_result_detail else {}
                pay_result_detail.update({'pay_success_result': wx_result})
                payment_record.pay_result_detail = json.dumps(pay_result_detail)
                payment_record.order.status = PaymentStatus[wx_result.get('trade_state')].value
                payment_record.save()
                payment_record.order.save()
                logger.info(f'订单{payment_record.order.id}兜底同步成功')
                # if wx_result.get('trade_state') == 'SUCCESS':
                #     send_bug_course_success_message.delay(payment_record.order.id)
                return PaymentStatus[wx_result.get('trade_state')], pay_result_detail

            elif payment_record.create_time.timestamp() + unpaid_days_threshold * 24 * 60 * 60 < time.time():
                payment_record.status = PaymentStatus.CLOSED.value
                payment_record.order.status = PaymentStatus.CLOSED.value
                payment_record.save()
            # else:
            #     payment_record.status = PaymentStatus.PENDING.value
            #     payment_record.order.status = PaymentStatus.PENDING.value
            #     payment_record.save()

    def query_alipay_result(self):
        pass
