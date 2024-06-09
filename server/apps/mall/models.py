from django.db import models

from utils.model import SoftModel
from apps.user_center.models import ExternalUser
from apps.system.models import User
from apps.ftz.models import Course, get_enum_choices, EnumConfig


class Product(SoftModel):
    """商品表"""
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    type = models.CharField('商品类型', max_length=20, choices=[])
    description = models.TextField('描述', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[])

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='product', service='type')
        self._meta.get_field('status').choices = get_enum_choices(module='product', service='status')

    @property
    def type_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='product', service='type', value=self.type)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None

    @property
    def status_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='product', service='status', value=self.status)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None

    def __str__(self):
        return self.name


# 订单模型
class Order(SoftModel):
    user = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[])
    order_uuid = models.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self._meta.get_field('status').choices = get_enum_choices(module='order', service='status')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product')
        ]
        # 联合索引
        indexes = [
            models.Index(fields=['user', 'product']),
        ]

    @property
    def status_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='order', service='status', value=self.status)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None

    def __str__(self):
        return f"Order {self.id}"


# 支付记录模型
class PaymentRecord(SoftModel):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    payment_method = models.CharField(max_length=10, choices=[])
    payment_date = models.DateTimeField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[])
    pay_id = models.CharField(max_length=20)
    pay_result_detail = models.CharField(max_length=1024, choices=[])

    def __init__(self, *args, **kwargs):
        super(PaymentRecord, self).__init__(*args, **kwargs)
        self._meta.get_field('status').choices = get_enum_choices(module='payment', service='status')
        self._meta.get_field('payment_method').choices = get_enum_choices(module='payment', service='type')

    @property
    def status_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='payment', service='status', value=self.status)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None

    @property
    def payment_method_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='payment', service='type', value=self.payment_method)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
