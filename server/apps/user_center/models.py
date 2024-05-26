from django.db import models

from utils.model import SoftModel, BaseModel


class ExternalUser(SoftModel):
    """
    外部用户
    """

    # 微信用户唯一标识
    openid = models.CharField(max_length=50, unique=True, null=True, blank=True,
                              help_text="微信用户唯一标识，用于身份验证和授权")
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

    def __str__(self):
        return f"{self.nickname}"


class ExternalOauth(SoftModel):
    """
    外部用户授权
    """

    user = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, verbose_name='用户id', blank=True, null=True)
    access_token = models.CharField(max_length=255, null=True, blank=True, help_text="授权的访问令牌")
    expires_in = models.IntegerField(null=True, blank=True, help_text="访问令牌过期时间")
    refresh_token = models.CharField(max_length=255, null=True, blank=True, help_text="刷新令牌")
    scope = models.CharField(max_length=128, null=True, blank=True, help_text="授权作用域")

    def __str__(self):
        return f"{self.user.nickname} - {self.expires_in}"
