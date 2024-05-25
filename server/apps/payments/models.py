# payments/models.py
from django.db import models
from users.models import User  # 假设已经定义了一个用户模型

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # 其他订单相关字段...

class PaymentRecord(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20)  # 支付平台，例如 'wechat' or 'alipay'
    transaction_id = models.CharField(max_length=100)  # 平台交易号
    status = models.CharField(max_length=20)  # 支付状态，例如 'success' or 'failed'
    # 其他支付记录相关字段...