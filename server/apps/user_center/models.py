from django.db import models

from apps.ftz.models import Lesson, TermCourse, Card
from utils.model import SoftModel, get_enum_choices, ExternalUser


class UserBehavior(SoftModel):
    """
    用户行为记录表，用户埋点上报
    """
    user = models.ForeignKey(ExternalUser, on_delete=models.CASCADE)  # 关联到Django的User模型
    channel = models.CharField(max_length=50, default='default')  # 渠道
    event_type = models.CharField(max_length=50)  # 事件类型
    event_value = models.CharField(max_length=256)  # 事件值
    event_detail = models.JSONField(null=True, blank=True)  # 事件详情，使用JSONField存储
    event_time = models.DateTimeField()  # 事件发生的时间戳
    event_report_time = models.DateTimeField(null=True, blank=True)  # 事件上报的时间戳

    class Meta:
        indexes = [
            models.Index(fields=['user', 'event_type', 'channel']),
        ]

    def __str__(self):
        return f"{self.user.id} - {self.event_type} - {self.report_time}"


class UserCollect(SoftModel):
    """
    用户收藏表
    """
    user = models.ForeignKey(ExternalUser, on_delete=models.CASCADE)  # 关联到Django的User模型
    collect_type = models.CharField('收藏类型', max_length=128, choices=[])
    event_id = models.BigIntegerField(verbose_name="收藏记录id")
    event_detail = models.JSONField(null=True, blank=True)  # 事件详情，使用JSONField存储
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True)  # 课时id
    term_course = models.ForeignKey(TermCourse, on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name="期课")  # 期课id
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, blank=True, null=True,
                             verbose_name="卡片")  # 卡片id

    class Meta:
        indexes = [
            models.Index(fields=['user', 'collect_type']),
        ]
        # unique_together = (
        #     ('user', 'collect_type', 'event_id'),
        # )

    def __init__(self, *args, **kwargs):
        super(UserCollect, self).__init__(*args, **kwargs)
        self._meta.get_field('collect_type').choices = get_enum_choices(module='user_collect', service='collect_type')

    def __str__(self):
        return f"{self.user.id} - {self.collect_type}"
