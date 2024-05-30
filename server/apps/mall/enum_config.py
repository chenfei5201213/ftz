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


class StudyStatus(Enum):
    LOCKED = 0, "已锁定"
    UNLOCKED = 1, "已解锁"
    IN_PROGRESS = 2, "学习中"
    COMPLETED = 3, "已学完"
