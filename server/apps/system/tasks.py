# Create your tasks here
from __future__ import absolute_import, unicode_literals
import logging
from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from django.utils.datetime_safe import datetime

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
    result = wx.send_bug_course_success_message(openid, product_info, order_id)
    logger.info(f"openid: {openid}, send_bug_course_success_message_result: {result}")


@shared_task
def class_reminder(*args, **kwargs):
    """
    上课提醒
    """
    # 获取当前时区的今天和明天的日期
    today = timezone.localtime(timezone.now()).date()
    tomorrow = today + timedelta(days=1)
    logger.info(f'args:{args}, kwargs:{kwargs}')
    # 将日期转换为datetime对象，并添加时区信息
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()), timezone.get_current_timezone())
    tomorrow_start = timezone.make_aware(datetime.combine(tomorrow, datetime.min.time()),
                                         timezone.get_current_timezone())
    # 创建一个 Q 对象，用于查询 open_time 大于等于当天0点且小于明天0点的记录
    time_query = Q(open_time__gte=today_start) & Q(open_time__lt=tomorrow_start)
    contents = CourseScheduleContent.objects.filter(time_query).all()
    logger.info(f"class_reminder_contents: {len(contents)}")
    user_lesson = {}
    for content in contents:
        try:
            only_key = f"{content.user_id}-{content.lesson_id}"
            if user_lesson.get(only_key):
                continue
            logger.info(f"user_lesson: {only_key} 满足消息通知")
            user_lesson[only_key] = 1
            user = content.user
            course = content.term_course.course
            open_time = content.open_time.astimezone(timezone.get_current_timezone()).strftime("%Y年%m月%d日")
            course_info = {
                'title': course.title,
                'open_time': open_time
            }
            if user.openid and user.id in kwargs.get('userid', []):
                send_class_reminder.delay(user.openid, course_info)
            else:
                msg = f'用户{user.id}不在推送白名单中' if user.openid else f'用户{user.id} 没有公众号注册，无法推送消息'
                logger.info(msg)
        except Exception as e:
            logger.exception(f'上课提醒异常: {repr(e)}')


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


@shared_task
def send_class_reminder(openid, course_info):
    wx = WchatTemplateMessage()
    result = wx.send_class_reminder(openid, course_info)
    logger.info(f"openid: {openid}, class_reminder_result: {result}")
