# Create your tasks here
from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from apps.ftz.models import CourseScheduleContent
from apps.ftz.serializers import CourseSerializer
from apps.mall.models import Order
from apps.mall.serializers import ProductSellSerializer
from apps.system.models import RequestLog
from utils.wechat.wechat_util import WchatTemplateMessage

logger = logging.getLogger(__name__)


@shared_task
def show():
    logger.info('ok')


@shared_task
def send_bug_course_success_message(order_id: int):
    order = Order.objects.filter(id=order_id).get()
    openid = order.user.openid
    if not openid:
        logger.error(f'用户{order.user.id} 没有公众号注册，无法推送消息')
        return
    product_info = ProductSellSerializer(order.product).data
    wx = WchatTemplateMessage()
    result = wx.send_bug_course_success_message(openid, product_info)
    logger.info(f"openid: {openid}, send_bug_course_success_message_result: {result}")


@shared_task
def class_reminder():
    """
    上课提醒
    """
    # 获取当天0点的时间
    today_start_time = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    # 获取明天0点的时间
    tomorrow_start_time = today_start_time + timezone.timedelta(days=1)
    # 创建一个 Q 对象，用于查询 open_time 大于等于当天0点且小于明天0点的记录
    time_query = Q(open_time__gte=today_start_time) & Q(open_time__lt=tomorrow_start_time)
    contents = CourseScheduleContent.objects.filter(time_query).all()
    user_lesson = {}
    for content in contents:
        try:
            only_key = f"{content.user_id}-{content.lesson_id}"
            if user_lesson.get('only_key'):
                content
            user_lesson[only_key] = 1
            user = content.user
            course = content.term_course.course
            open_time = content.open_time.strftime("%Y年%m月%d日")
            course_info = {
                'title': course.title,
                'open_time': open_time
            }
            wx = WchatTemplateMessage()
            result = wx.send_class_reminder(user.openid, course_info)
            logger.info(f"openid: {user.openid}, send_bug_course_success_message_result: {result}")
        except Exception as e:
            logger.exception(f'上课提醒异常')


@shared_task
def save_request_log(method, path, remote_addr, query_params, body_params, duration):
    try:
        RequestLog.objects.create(
            method=method,
            path=path,
            remote_addr=remote_addr,
            query_params=query_params,
            body_params=body_params,
            duration=duration
        )
    except Exception as e:
        logger.exception(f"写入日志异常")
