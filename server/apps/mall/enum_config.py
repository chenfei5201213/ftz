from enum import Enum


class OrderStatus(Enum):
    FREE = 'free'
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    CLOSED = 'closed'


class PaymentStatus(Enum):
    INIT = 'init'
    PENDING = 'pending'
    PAID = 'paid'
    SUCCESS = 'paid'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    CLOSED = 'closed'


class ProductStatus(Enum):
    OnSale = ('1', '上架')
    OffSale = ('2', '下架')


class ProductType(Enum):
    STANDARD = ('1', '正价商品')
    FREE = ('2', '0元赠品')


class PaymentMethod(Enum):
    WECHAT = 'wechat'
    ALIPAY = 'alipay'
    FREE = 'free'


class StudyStatus(Enum):
    LOCKED = 0, "已锁定"
    UNLOCKED = 1, "已解锁"
    IN_PROGRESS = 2, "学习中"
    COMPLETED = 3, "已学完"


class UserType(Enum):
    Guest = 1, "游客"
    Member = 2, "会员"


if __name__ == '__main__':
    print(StudyStatus.__members__)
