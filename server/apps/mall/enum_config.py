from enum import Enum


class OrderStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class PaymentStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class ProductStatus(Enum):
    OnSale = ('1', '上架')
    OffSale = ('2', '下架')


class PaymentMethod(Enum):
    WECHAT = 'wechat'
    ALIPAY = 'alipay'