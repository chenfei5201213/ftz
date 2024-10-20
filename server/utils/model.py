from django.db import models
import django.utils.timezone as timezone
from django.db.models.query import QuerySet
from simple_history.models import HistoricalRecords


# 自定义软删除查询基类


class SoftDeletableQuerySetMixin(object):
    '''
    QuerySet for SoftDeletableModel. Instead of removing instance sets
    its ``is_deleted`` field to True.
    '''

    def delete(self, soft=True):
        '''
        Soft delete objects from queryset (set their ``is_deleted``
        field to True)
        '''
        if soft:
            self.update(is_deleted=True)
        else:
            return super(SoftDeletableQuerySetMixin, self).delete()


class SoftDeletableQuerySet(SoftDeletableQuerySetMixin, QuerySet):
    pass


class SoftDeletableManagerMixin(object):
    '''
    Manager that limits the queryset by default to show only not deleted
    instances of model.
    '''
    _queryset_class = SoftDeletableQuerySet

    def get_queryset(self, all=False):
        '''
        Return queryset limited to not deleted entries.
        '''
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints
        if all:
            return self._queryset_class(**kwargs)
        return self._queryset_class(**kwargs).filter(is_deleted=False)


class SoftDeletableManager(SoftDeletableManagerMixin, models.Manager):
    pass


class BaseModel(models.Model):
    """
    基本表
    """
    create_time = models.DateTimeField(
        default=timezone.now, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(
        auto_now=True, verbose_name='修改时间', help_text='修改时间')
    is_deleted = models.BooleanField(
        default=False, verbose_name='删除标记', help_text='删除标记')

    class Meta:
        abstract = True


class SoftModel(BaseModel):
    """
    软删除基本表
    """

    class Meta:
        abstract = True

    objects = SoftDeletableManager()

    def delete(self, using=None, soft=True, *args, **kwargs):
        '''
        这里需要真删除的话soft=False即可
        '''
        if soft:
            self.is_deleted = True
            self.save(using=using)
        else:

            return super(SoftModel, self).delete(using=using, *args, **kwargs)


class EnumConfig(SoftModel):
    """
    枚举配置表
    """
    module = models.CharField('模块', max_length=128, blank=False)
    service = models.CharField('业务', max_length=128, blank=False)
    name = models.CharField('名称', max_length=128, blank=False)
    value = models.CharField('值', max_length=128, blank=False)
    description = models.TextField('描述', blank=True)
    history = HistoricalRecords()

    class Meta:
        app_label = 'ftz'  # 替换为实际的应用名称


class ExternalUser(SoftModel):
    """
    外部用户
    """

    # 微信用户唯一标识
    openid = models.CharField(max_length=50, unique=True, null=True, blank=True,
                              help_text="微信公众号用户唯一标识，用于身份验证和授权")
    mini_openid = models.CharField(max_length=50, unique=True, null=True, blank=True,
                                   help_text="微信小程序用户唯一标识，用于身份验证和授权")
    unionid = models.CharField(max_length=50, unique=True, null=True, blank=True,
                               help_text="微信开放平台提供的一个唯一标识符，用于标识微信开放平台下的用户")
    # 用户昵称
    nickname = models.CharField(max_length=100, null=True, blank=True, help_text="用户的昵称，用于展示和称呼")
    # 用户头像URL
    avatar = models.CharField(max_length=255, null=True, blank=True, help_text="用户的头像URL，用于展示用户形象")
    # 用户性别（1：男，2：女）
    gender = models.CharField(max_length=10, null=True, blank=True, help_text="用户的性别，用于个性化展示")
    # 用户国家
    country = models.CharField(max_length=50, null=True, blank=True, help_text="用户的国家，用于定位用户")
    # 用户省份
    province = models.CharField(max_length=50, null=True, blank=True, help_text="用户的省份，用于定位用户")
    # 用户城市
    city = models.CharField(max_length=50, null=True, blank=True, help_text="用户的城市，用于定位用户")
    # 创建时间
    create_time = models.DateTimeField(auto_now_add=True, help_text="用户创建时间，自动添加")
    # 用户名（可选，如果需要，可以设置为唯一）
    username = models.CharField(max_length=150, unique=True, null=True, help_text='用户名称')

    source_system = models.CharField(max_length=100, null=True, blank=True, help_text="用户来源系统")
    # 手机号码（可选）
    phone_number = models.CharField(max_length=15, null=True, blank=True, help_text="用户的手机号码，用于登录和身份识别")

    # 用户简介（可选）
    bio = models.TextField(null=True, blank=True, help_text="用户简介，用于展示用户信息")
    # 电子邮件（可选，如果需要，可以设置为唯一）
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True,
                              help_text="用户的电子邮件地址，用于登录和身份识别")

    # 用户密码（可选，如果需要，可以使用Django的User.set_password方法）
    password = models.CharField(max_length=128, null=True, blank=True, help_text="用户密码，用于登录和身份识别")

    class Meta:
        app_label = 'user_center'  # 替换为实际的应用名称

    def __str__(self):
        return f"{self.unionid}" or f"{self.id}"

    def is_authenticated(self):
        return True


class ExternalOauth(SoftModel):
    """
    外部用户授权
    """

    user = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, verbose_name='用户id', blank=True, null=True)
    access_token = models.CharField(max_length=255, null=True, blank=True, help_text="授权的访问令牌")
    expires_in = models.IntegerField(null=True, blank=True, help_text="访问令牌过期时间")
    refresh_token = models.CharField(max_length=255, null=True, blank=True, help_text="刷新令牌")
    scope = models.CharField(max_length=128, null=True, blank=True, help_text="授权作用域")

    class Meta:
        app_label = 'user_center'  # 替换为实际的应用名称

    def __str__(self):
        return f"{self.user.nickname} - {self.expires_in}"


def get_enum_choices(module: str, service: str):
    enum_choices = EnumConfig.objects.filter(module=module, service=service).values_list('value', 'name')
    return enum_choices
