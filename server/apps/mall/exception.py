from utils.custom_exception import FtzException


class OrderException(FtzException):
    pass


class OrderPayException(FtzException):
    pass


class ProductException(FtzException):
    pass


class InsertTermContext(FtzException):
    pass


class InsertTermStudent(FtzException):
    pass
