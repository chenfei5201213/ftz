import requests
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
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
        unionid = decoded_token['unionid']

        try:
            user = ExternalUser.objects.get(unionid=unionid)
        except ExternalUser.DoesNotExist:
            raise AuthenticationFailed({"detail": "用户不存在"})

        return (user, token)


class ExternalUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(ExternalUserTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['unionid'] = user.unionid
        # ...

        return token
