from enum import Enum


class ErrorCode(Enum):
    DefaultError = 100000  # '自定义未知异常'

    ProductException = 100100  # '商品未知异常'
    ProductNotExit = 100101  # '商品不存在'
    ProductOff = 100102  # '商品已下线'
    ProductNotFree = 100103  # 非特价商品
    OrderException = 100200  # '订单未知异常'
    OrderNotExit = 100201  # '订单不存在'
    OrderDuplication = 100202  # '订单已存在'
    OrderCreateException = 100203  # '订单已存在'
    OrderNotPaidException = 10024  # '订单未支付'
    OrderPayCreateException = 10025  # '订单未支付'

    TermCourseException = 100300  # 期课未知异常

    ExternalUserException = 100400  # 用户未知异常
    ExternalUserDuplication = 100400  # 用户已存在


class FtzException(Exception):
    def __init__(self, message, error_code=ErrorCode.DefaultError.value):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.error_code}: {self.message}"
