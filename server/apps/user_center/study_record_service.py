# encoding: utf-8
"""
@software: PyCharm
@file: study_record_service.py
@time: 2024/9/18 08:25
@desc: 个人中心
"""
import math
from datetime import timedelta

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate

from apps.ftz.models import CourseScheduleContent, Card, TermCourse
from apps.mall.enum_config import StudyStatus, OrderStatus
from apps.mall.models import Order
from apps.user_center.models import ExternalUser
from component import generate_month_calendar
from component.cache.lesson_cache_helper import LessonCacheHelper


class StudyRecordService:
    def __init__(self, user: ExternalUser):
        self.user = user

    def get_study_total_duration(self):
        """获取总的学习时长"""
        # 获取用户学习的所有素材的学习内容记录，并直接关联到卡片
        study_contents = CourseScheduleContent.objects.filter(user=self.user, study_status=StudyStatus.COMPLETED.value[
            0]).select_related('card')

        # 获取所有相关卡片的ID
        card_ids = study_contents.values_list('card_id', flat=True).distinct()

        # 预先计算每个卡片的总计划耗时和素材总数，并存储在字典中
        card_planned_durations = {}
        for card in Card.objects.filter(id__in=card_ids):
            card_planned_durations[card.id] = {
                # 'planned_duration': card.study_duration,
                # 'material_count': card.study_materials.count(),
                'study_material_cost_avg': card.study_duration / card.study_materials.count()
            }

        # 初始化总计划耗时
        total_planned_duration = 0

        # 遍历每条学习内容记录
        for content in study_contents:
            # 获取对应的卡片ID
            card_id = content.card_id
            # 直接从字典中获取卡片的计划耗时和素材总数
            # card_planned_duration = card_planned_durations[card_id]['planned_duration']
            # material_count = card_planned_durations[card_id]['material_count']
            # 计算每个素材的计划耗时并累加到总计划耗时
            total_planned_duration += card_planned_durations[card_id]['study_material_cost_avg']

        # 由于每个素材都会被计算一次，我们乘以素材的数量来得到总计划耗时
        # total_planned_duration *= study_contents.count()
        return math.ceil(total_planned_duration)

    def get_study_total_days(self):
        """
        获取学习天数
        """
        unique_study_days = CourseScheduleContent.objects.filter(
            user=self.user,
            study_status=StudyStatus.COMPLETED.value[0]
        ).annotate(
            study_day=TruncDate('update_time')  # 将日期时间字段截断到日期
        ).values('study_day').annotate(
            count=Count('id')  # 对每天的学习记录进行计数
        ).count()  # 统计不同的学习天数
        return unique_study_days

    def get_study_calendar(self, specific_year: int, specific_month: int):
        """
        获取指定月的学习情况
        """
        # term_course = Order.objects.filter(
        #     Q(product__term_course__course_start__year=specific_year)
        #     &Q(product__term_course__course_start__month=specific_month),
        #     user=self.user, status=OrderStatus.PAID.value, total_amount__ge=0).select_related('product__term_course')
        # term_courses = TermCourse.objects.filter(
        #     Q(course_start__year=specific_year) & Q(course_start__month=specific_month)
        # )

        # 获取该用户的订单
        contents = CourseScheduleContent.objects.filter(
            Q(term_course__course_start__year=specific_year)
            & Q(term_course__course_start__month=specific_month),
            user=self.user).all()
        calendar_dict = generate_month_calendar(specific_year, specific_month)
        for content in contents:
            open_time = content.open_time.strftime('%Y-%m-%d')
            lesson_id = content.lesson_id
            if not calendar_dict[open_time].get('count'):
                calendar_dict[open_time]['count'] = LessonCacheHelper(lesson_id).get_lesson_material_count()
            if content.finish_time and content.finish_time - content.open_time <= timedelta(days=1):
                calendar_dict[open_time]['finish_count'] = calendar_dict[open_time].get('finish_count', 0) + 1
        return calendar_dict
