import json
import time
import uuid
from concurrent.futures._base import LOGGER

from wechatpayv3 import WeChatPay, WeChatPayType

from apps.mall.models import Order, PaymentRecord
from apps.user_center.models import ExternalUser
from server.settings import MCHID, PRIVATE_KEY, CERT_SERIAL_NO, APIV3_KEY, APPID, NOTIFY_URL, CERT_DIR, PARTNER_MODE, \
    PROXY, TIMEOUT


class WeChatPayService:
    def __init__(self):
        self.wxpay = self.wx_init()

    def wx_init(self):
        wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=MCHID,
            private_key=PRIVATE_KEY,
            cert_serial_no=CERT_SERIAL_NO,
            apiv3_key=APIV3_KEY,
            appid=APPID,
            notify_url=NOTIFY_URL,
            cert_dir=CERT_DIR,
            logger=LOGGER,
            partner_mode=PARTNER_MODE,
            proxy=PROXY,
            timeout=TIMEOUT
        )
        return wxpay

    def create_jsapi_order(self, order: Order, user: ExternalUser):
        # 调用微信支付API创建订单
        out_trade_no = order.order_uuid
        description = order.product.name
        amount = int(order.total_amount * 100)
        payer = {'openid': user.openid}
        code, message = self.wxpay.pay(
            description=description,
            out_trade_no=out_trade_no,
            amount={'total': amount},
            pay_type=WeChatPayType.JSAPI,
            payer=payer
        )
        result = json.loads(message)
        if code in range(200, 300):
            prepay_id = result.get('prepay_id')
            timestamp = str(int(time.time()))
            noncestr = str(uuid.uuid4()).replace('-', '')
            package = 'prepay_id=' + prepay_id
            sign = self.wxpay.sign([APPID, timestamp, noncestr, package])
            signtype = 'RSA'
            return {'code': 0, 'result': {
                'appId': APPID,
                'timeStamp': timestamp,
                'nonceStr': noncestr,
                'package': 'prepay_id=%s' % prepay_id,
                'signType': signtype,
                'paySign': sign
            }}
        else:
            return {'code': -1, 'result': result}

    def query_order(self, out_trade_no):
        # 查询微信支付订单状态
        return self.wxpay.query(out_trade_no=out_trade_no)

    def callback(self, headers, data):
        result = self.wxpay.callback(headers, data)
        if result and result.get('event_type') == 'TRANSACTION.SUCCESS':
            resp = result.get('resource')
            transaction_id = resp.get('transaction_id')
            trade_type = resp.get('trade_type')
            trade_state = resp.get('trade_state')
            trade_state_desc = resp.get('trade_state_desc')
            bank_type = resp.get('bank_type')
            attach = resp.get('attach')
            success_time = resp.get('success_time')
            payer = resp.get('payer')
            amount = resp.get('amount').get('total')
            return {'code': 'SUCCESS', 'data': result}
        else:
            return {'code': 'FAILED', 'message': '失败', 'data': result}
