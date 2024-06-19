import json
import logging
import uuid

from django.db import IntegrityError
from django.utils import timezone

from utils.custom_exception import ErrorCode
from .exception import OrderException, ProductException, InsertTermContext, OrderPayException
from .models import Product, Order, PaymentRecord
from .serializers import ProductSerializer, OrderSerializer, PaymentRecordSerializer
from ..ftz.service import TermCourseService

from ..payments.services.wechat_pay import WeChatPayService
from ..user_center.models import ExternalUser
from .enum_config import OrderStatus, PaymentStatus, ProductStatus, PaymentMethod, UserType, StudyStatus


logger = logging.getLogger(__name__)


class ProductService:
    def get_products(self):
        # 获取所有商品信息
        products = Product.objects.all()
        # 序列化商品信息
        serializer = ProductSerializer(products, many=True)
        return serializer.data

    def create_order(self, product_id, user_id, count=1):
        # 获取商品和用户信息
        try:
            product = Product.objects.get(id=product_id)
            if product.is_deleted or product.status != ProductStatus.OnSale.value[0]:
                logger.info(f"product: {product}")
                raise ProductException("商品不存在或者已下架", ErrorCode.ProductOff.value)
            user = ExternalUser.objects.get(id=user_id)
            total_amount = product.price * count
            # 创建订单
            full_uuid = uuid.uuid4()

            # 提取UUID的一部分作为32位字符串
            # 这里我们取UUID的前16个字符和后16个字符组合
            uuid_32bit = str(full_uuid)[:16] + str(full_uuid)[16:32]
            order = Order.objects.create(user=user,
                                         product=product,
                                         total_amount=total_amount,
                                         order_uuid=uuid_32bit,
                                         status=OrderStatus.PENDING.value)
            serializer = OrderSerializer(order)
            term_service = TermCourseService(user.id, product.course.id)
            term_service.insert_student()
            term_service.insert_student_context()

            return serializer.data
        except Order.DoesNotExist:
            logger.error(f"订单不存在", ErrorCode.OrderNotExit.value)
            raise OrderException("订单不存在")
        except Product.DoesNotExist:
            raise ProductException("商品不存在", ErrorCode.ProductNotExit.value)
        except IntegrityError:
            order = Order.objects.filter(user=user_id, product=product_id).first()
            data = {
                'order_info': OrderSerializer(order).data if order else {}
            }
            payment_record = PaymentRecord.objects.filter(order=order.id).order_by('-id').first()
            data.update({
                'payment_record_info': PaymentRecordSerializer(payment_record).data if payment_record else {}
            })
            raise OrderException('订单已存在，请无重复创建', ErrorCode.OrderDuplication.value, data=data)
        except InsertTermContext:
            return serializer.data
        except Exception as e:
            logger.exception(f'创建订单异常')
            raise e

    def create_payment_record(self, user: ExternalUser, order_id, amount, payment_method=PaymentMethod.WECHAT.value):
        try:
            # 获取订单信息
            order = Order.objects.get(id=order_id)
            if payment_method == PaymentMethod.WECHAT.value:
                wx_pay_service = WeChatPayService()
                result = wx_pay_service.create_jsapi_order(order, user)
                logger.info(f"order: {order_id}, 创建微信订单结果: {result}")
                if result.get('code') == 0:
                    # 创建支付记录
                    payment_record = PaymentRecord.objects.create(order=order,
                                                                  payment_method=payment_method,
                                                                  amount=amount,
                                                                  status=PaymentStatus.INIT.value)

                    payment_record.status = PaymentStatus.PENDING.value
                    payment_record.pay_result_detail = json.dumps(result)
                    payment_record.pay_id = result['result']['package'].split('=')[1]
                    payment_record.save()
                else:
                    raise OrderPayException('支付订单创建失败', ErrorCode.OrderPayCreateException.value)
            elif payment_method == PaymentMethod.FREE.value:
                payment_record = PaymentRecord.objects.create(order=order,
                                                              payment_method=payment_method,
                                                              amount=0,
                                                              status=PaymentStatus.PAID.value,
                                                              pay_time=timezone.now())
                order.status = OrderStatus.PAID.value
                order.save()
            # 返回支付记录信息
            data = PaymentRecordSerializer(payment_record).data
            # data['pay_result_detail'] = json.loads(data.get('pay_result_detail', '{}'))
            return data
        except Order.DoesNotExist:
            raise OrderException('订单不存在', ErrorCode.OrderNotExit.value)
        except Exception as e:
            logger.exception('创建支付记录异常')
            raise e


class OrderService:
    def get_order(self, order_id):
        # 获取订单信息
        order = Order.objects.get(id=order_id)
        # 返回订单信息
        serializer = OrderSerializer(order)
        return serializer.data

    def update_order_status(self, order_id, status):
        # 获取订单信息
        order = Order.objects.get(id=order_id)
        # 更新订单状态
        order.status = status
        order.save()


class PaymentService:
    def get_payment_records(self):
        # 获取所有支付记录信息
        payment_records = PaymentRecord.objects.all()
        # 序列化支付记录信息
        serializer = PaymentRecordSerializer(payment_records, many=True)
        return serializer.data

    def create_payment_record(self, order_id, payment_method, amount):
        # 获取订单信息
        order = Order.objects.get(id=order_id)
        # 创建支付记录
        payment_record = PaymentRecord.objects.create(order=order, payment_method=payment_method, amount=amount)
        # 返回支付记录信息
        serializer = PaymentRecordSerializer(payment_record)
        return serializer.data
