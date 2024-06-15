class OrderEvent:
    def __init__(self):
        pass

    def order_pay_success(self):
        """
        订单支付成功后进行的操作
        """
        # 1. 发送支付成功通知
