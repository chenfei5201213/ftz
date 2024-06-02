import requests
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import UntypedToken

from apps.user_center.models import ExternalUser
from server.settings import APPID, APIV3_KEY

UserModel = get_user_model()


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get(
                Q(username=username) | Q(phone=username) | Q(email=username))
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class WeChatBackend(ModelBackend):
    def authenticate(self, request, code=None):
        if code is None:
            return

        # 使用 code 换取 access_token 和 openid
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': APPID,
            'secret': APIV3_KEY,
            'code': code,
            'grant_type': 'authorization_code',
        }
        response = requests.get(url, params=params)
        data = response.json()

        if 'errcode' in data:
            # 处理错误
            return

        access_token = data.get('access_token')
        openid = data.get('openid')

        # 使用 access_token 和 openid 获取用户信息
        user_info_url = 'https://api.weixin.qq.com/sns/userinfo'
        user_info_params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN',
        }
        user_info_response = requests.get(user_info_url, params=user_info_params)
        user_info = user_info_response.json()

        if 'errcode' in user_info:
            # 处理错误
            return

        # 根据 openid 查找或创建用户
        try:
            user = UserModel.objects.get(username=openid)
        except UserModel.DoesNotExist:
            # 如果用户不存在，则创建新用户
            user = UserModel.objects.create_user(username=openid)
            # 可以在这里设置用户的更多信息，例如昵称、头像等
            user.nickname = user_info.get('nickname')
            user.save()

        return user


class ExternalUserAuth(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return None

        try:

            decoded_token = UntypedToken(token)
            # decoded_token = untyped_token.decode()
        except (TokenError, InvalidToken):
            raise AuthenticationFailed({"detail": "token 无效或已过期"})
        openid = decoded_token['openid']

        try:
            user = ExternalUser.objects.get(openid=openid)
        except ExternalUser.DoesNotExist:
            raise AuthenticationFailed({"detail": "用户不存在"})

        return (user, token)


class ExternalUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(ExternalUserTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['openid'] = user.openid
        # ...

        return token
