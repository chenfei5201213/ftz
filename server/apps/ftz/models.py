from django.db import models
from simple_history.models import HistoricalRecords

from apps.user_center.models import ExternalUser
from utils.model import SoftModel, EnumConfig, get_enum_choices


class Tag(SoftModel):
    """
    标签表
    """
    name = models.CharField('名称', max_length=128, blank=False)




class Course(SoftModel):
    """
    课程表
    """
    # course_type_choices = (
    #     ('公开课', '公开课'),
    #     ('入门课', '入门课'),
    #     ('进阶课', '进阶课'),
    # )
    title = models.CharField('课程标题', max_length=128, unique=True, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=[])
    lesson_count = models.IntegerField('课程数量', default=0)
    history = HistoricalRecords()

    def __init__(self, *args, **kwargs):
        super(Course, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='course', service='type')

    @property
    def type_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='course', service='type', value=self.type)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None


# class Word(SoftModel):
#     """
#     单词表
#     """
#     pass
#
#
# class Grammar(SoftModel):
#     """
#     语法表
#     """
#     pass


class StudyMaterial(SoftModel):
    """
    学习素材表
    """
    title = models.CharField('标题', max_length=128, blank=False)
    sub_title = models.CharField('副标题', max_length=512, blank=True)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=[])
    context = models.TextField('素材内容', blank=True, max_length=65535)
    # words = models.ManyToManyField(Word, blank=True, verbose_name='单词', related_name='words')
    # grammars = models.ManyToManyField(Grammar, blank=True, verbose_name='语法', related_name='grammars')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签', related_name='tags')
    history = HistoricalRecords()

    def __init__(self, *args, **kwargs):
        super(StudyMaterial, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='material', service='type')

    @property
    def type_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='material', service='type', value=self.type)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None


class Card(SoftModel):
    """
    卡片表
    """
    title = models.CharField('课时标题', max_length=128, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=[])
    status = models.CharField('状态', choices=[], default='0')
    card_core_image = models.CharField('核心图', max_length=128, blank=True)
    group_name = models.CharField('卡片分组名称', max_length=512, blank=True)
    topic = models.CharField('话题', max_length=128, blank=True)
    difficulty = models.CharField('难度', max_length=32, choices=[], blank=False, default='easy')
    study_materials = models.ManyToManyField(StudyMaterial, blank=True, verbose_name='素材',
                                             related_name='study_materials')
    history = HistoricalRecords()

    # , through='CardStudyMaterial'
    # study_material_ids = models.JSONField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Card, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='card', service='type')
        self._meta.get_field('difficulty').choices = get_enum_choices(module='card', service='difficulty')
        self._meta.get_field('status').choices = get_enum_choices(module='card', service='status')

    @property
    def type_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='card', service='type', value=self.type)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None

    @property
    def difficulty_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='card', service='difficulty', value=self.difficulty)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None

    @property
    def status_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='card', service='status', value=self.status)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None


# class CardStudyMaterial(models.Model):
#     card = models.ForeignKey(Card, on_delete=models.CASCADE)
#     studymaterial = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE)
#     id = models.AutoField(primary_key=True)  # 自增 ID 字段
#
#     class Meta:
#         db_table = 'ftz_card_study_materials'
#         ordering = ['id']  # 按照自增 ID 排序


class Lesson(SoftModel):
    """
    课时表
    """
    # lesson_type_choices = (
    #     ('编程课', '编程课'),
    #     ('编程卡', '编程卡'),
    # )
    title = models.CharField('课时标题', max_length=128, blank=False)
    description = models.TextField('描述', blank=True)
    type = models.CharField('课程类型', max_length=128, choices=[])
    lesson_number = models.IntegerField('顺序', blank=False)
    group_name = models.CharField('课时分组', default='默认分组', max_length=512)
    version = models.CharField('版本号')

    cards = models.ManyToManyField(Card, blank=True, verbose_name='卡片', related_name='cards')
    course_id = models.ForeignKey(Course, on_delete=models.SET_NULL, verbose_name='课程', blank=True, null=True,
                                  related_name='course')
    history = HistoricalRecords()

    def __init__(self, *args, **kwargs):
        super(Lesson, self).__init__(*args, **kwargs)
        self._meta.get_field('type').choices = get_enum_choices(module='lesson', service='type')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course_id', 'lesson_number'], name='unique_course_lesson_number')
        ]
        # 联合索引
        indexes = [
            models.Index(fields=['course_id', 'lesson_number']),
        ]

    @property
    def type_description(self):
        try:
            enum_config = EnumConfig.objects.get(module='lesson', service='type', value=self.type)
            return enum_config.name
        except EnumConfig.DoesNotExist:
            return None


class Survey(SoftModel):
    """
    调查表，存储调查的基本信息。
    """
    title = models.CharField(max_length=200, verbose_name="调查标题")
    description = models.TextField(verbose_name="调查描述")
    start_time = models.DateTimeField(verbose_name="开始时间")
    expiry_time = models.DateTimeField(verbose_name="截止日期")

    class Meta:
        verbose_name = "调查"
        verbose_name_plural = "调查列表"


class Question(SoftModel):
    """
    题目表，存储单个调查的具体问题。
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name="调查问卷")
    question_text = models.TextField(verbose_name="问题内容")
    question_type = models.CharField(max_length=20, verbose_name="问题类型")
    options = models.TextField(verbose_name="选项", help_text="JSON格式存储选项")

    class Meta:
        verbose_name = "问题"
        verbose_name_plural = "问题列表"


class UserResponse(SoftModel):
    """
    用户回答表，记录用户对调查问题的回答。
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name="调查问卷", related_name='r_survey')
    user = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, blank=True, null=True)  # 用户id
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="问题", related_name='r_question')
    answer = models.TextField(verbose_name="回答")
    response_time = models.DateTimeField(verbose_name="回答时间")

    class Meta:
        verbose_name = "用户回答"
        verbose_name_plural = "用户回答列表"
        # unique_together = ('survey', 'user', 'question')  # 在模型中设置联合唯一约束


class TermCourse(SoftModel):
    """
    期课表
    """
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, default=3, null=True, verbose_name="课程",
                               related_name='schedules')  # 课程id
    term_number = models.IntegerField(blank=True)  # 期数
    term_type = models.CharField(max_length=100, blank=True)  # 期课类型
    version = models.CharField(max_length=100)  # 版本
    total_days = models.IntegerField(blank=True)  # 总天数
    enrollment_start = models.DateTimeField('报课开始时间', blank=True, null=True)
    enrollment_end = models.DateTimeField('报课结束时间', blank=True, null=True)
    course_start = models.DateTimeField('课程开始时间', blank=True, null=True)
    course_end = models.DateTimeField('课程结束时间', blank=True, null=True)
    teacher = models.CharField(max_length=100, blank=True)  # 老师
    teacher_qr_code = models.CharField(max_length=100, blank=True)  # 老师二维码
    assistant_teacher = models.CharField(max_length=100, blank=True)  # 助教老师
    assistant_teacher_qr_code = models.CharField(max_length=100, blank=True)  # 助教老师二维码
    history = HistoricalRecords()

    # 联合唯一约束
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'term_number'], name='unique_course_schedule')
        ]
        # 联合索引
        indexes = [
            models.Index(fields=['course', 'term_number']),
        ]

    def __str__(self):
        return f"{self.course} - {self.term_number}"


class CourseScheduleStudent(SoftModel):
    """
    期课学员表
    """
    user = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, blank=True, null=True)  # 用户id
    exp_time = models.DateTimeField('过期时间', blank=True, null=True)  # 过期时间
    study_status = models.IntegerField(blank=True, null=True)  # 学习状态
    term_course = models.ForeignKey(TermCourse, on_delete=models.SET_NULL, blank=True, null=True)  # 期课id

    def __str__(self):
        return f"{self.user} - {self.term_course}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'term_course'], name='unique_user_term_course')
        ]
        # 联合索引
        indexes = [
            models.Index(fields=['user', 'term_course']),
        ]


class CourseScheduleContent(SoftModel):
    """
    期课内容表
    """
    user = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, blank=True, null=True)  # 用户id
    lesson_number = models.IntegerField()  # 课时序号
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True)  # 课时id
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.SET_NULL, blank=True, null=True)  # 学习素材
    open_time = models.DateTimeField()  # 开课时间
    finish_time = models.DateTimeField(null=True, blank=True)  # 完成时间
    study_status = models.IntegerField(null=True, blank=True)  # 学习状态
    term_course = models.ForeignKey(TermCourse, on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name="期课")  # 期课id
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, blank=True, null=True,
                             verbose_name="卡片")  # 卡片id


class UserStudyRecord(SoftModel):
    """
    用户学习记录表
    """
    user = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, blank=True, null=True)  # 用户id
    lesson_number = models.IntegerField()  # 课时序号
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True)  # 课时id
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.SET_NULL, blank=True, null=True)  # 学习素材
    study_duration = models.IntegerField()  # 学习时长

    def __str__(self):
        return f"{self.user} - {self.lesson_number}"
