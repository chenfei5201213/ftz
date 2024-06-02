import hashlib
import logging

from django.core.cache import cache
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import filters, status
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from utils.wechat_util import WechatUtil, WechatMiniUtil

from server import settings

from .models import ExternalUser, ExternalOauth
from .serializers import ExternalUserSerializer, ExternalOauthSerializer
from .service import TermCourseService, ExternalUserService
from ..ftz.serializers import TermCourseSerializer
from ..system.authentication import ExternalUserTokenObtainPairSerializer, ExternalUserAuth
from ..system.permission import ExternalUserPermission

logger = logging.getLogger('__name__')


class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# Create your views here.
class UserLogin(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        redirect_url = WechatUtil.wechat_login()
        return Response(data={'redirect_url': redirect_url})


class WechatLogin(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        logger.info(f"code: ={code}")
        if not code:
            return Response("授权失败", status=400)
        access_token_data = WechatUtil.access_token(code)
        if access_token_data:
            return Response(data=access_token_data)
        logger.info(f"access_token_data: {access_token_data}")
        user_info = WechatUtil.get_user_info(access_token_data['access_token'], access_token_data['openid'])
        logger.info(f"user_info: {user_info}")
        return Response(data=user_info)


class WechatMiniLogin(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        logger.info(f"code: ={code}")
        code_token_redis_key = f'tk:code:{code}'
        if not code:
            return Response("授权失败", status=400)
        wx = WechatMiniUtil()
        user_info = wx.login(code)

        if not user_info:
            return Response("获取用户信息失败", status=400)
        user_service = ExternalUserService(user_info['openid'])
        _user = user_service.get_user()
        if not _user:
            _user = user_service.save(user_info)

        # 生成JWT Token
        token = ExternalUserTokenObtainPairSerializer.get_token(_user)
        result = {'access': str(token.access_token), 'refresh': str(token)}
        cache.set(code_token_redis_key, result, timeout=7200)
        return Response({'access': str(token.access_token), 'refresh': str(token)})


class WechatCallbackLogin(GenericAPIView):
    serializer_class = ExternalUserTokenObtainPairSerializer  # 设置serializer_class属性
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        code_token_redis_key = f'tk:code:{code}'
        logger.info(f"code: ={code}")
        cache_data = cache.get(code_token_redis_key)
        if cache_data:
            return Response(data=cache_data)
        if not code:
            return Response("授权失败", status=400)
        access_token_data = WechatUtil.access_token(code)
        if access_token_data.get("errcode"):
            return Response(data=access_token_data)
        logger.info(f"access_token_data: {access_token_data}")
        user_info = WechatUtil.get_user_info(access_token_data['access_token'], access_token_data['openid'])
        # user_info = {'openid': 'o77756JY-IHm6zh-Ez3HVsLJIKvB', 'nickname': 'é£\x8eä¸\xadéª\x84å\xad\x90', 'sex': 0,
        #              'language': '', 'city': '', 'province': '', 'country': '',
        #              'headimgurl': 'https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLjpEibWYayXiaIQzqv4QLlkGmJf4iaU1G8A3gzEeohlJyoA8YX0Rsbx5685HlIpFeWTgV661FFXqPdA/132',
        #              'privilege': []}
        if not user_info:
            return Response("获取用户信息失败", status=400)
        user_service = ExternalUserService(user_info['openid'])
        _user = user_service.get_user()
        if not _user:
            _user = user_service.save(user_info)

        # 生成JWT Token
        token = ExternalUserTokenObtainPairSerializer.get_token(_user)
        result = {'access': str(token.access_token), 'refresh': str(token)}
        cache.set(code_token_redis_key, result, timeout=7200)
        return Response({'access': str(token.access_token), 'refresh': str(token)})


class WechatEchoStr(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            data = request.query_params
            signature = data.get('signature')
            timestamp = data.get('timestamp')
            nonce = data.get('nonce')
            echostr = data.get('echostr')
            token = settings.WECHAT_TOKEN  # 从 Django 设置中获取 Token

            # 验证消息的确来自微信服务器
            list_ = [token.encode('utf-8'), timestamp.encode('utf-8'), nonce.encode('utf-8')]
            list_.sort()
            sha1 = hashlib.sha1()
            # map(sha1.update, list_)
            [sha1.update(item) for item in list_]
            hashcode = sha1.hexdigest()

            if hashcode == signature:
                return HttpResponse(echostr)
            else:
                return HttpResponse('')  # 返回 400 错误
        except Exception as e:
            return Response({"error": str(e)}, status=500)  # 返回 500 错误


class ExternalUserView(ModelViewSet):
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = ExternalUser.objects.all()
    serializer_class = ExternalUserSerializer
    search_fields = ['nickname', 'username', 'phone_number']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    # filterset_fields = ['type']


class ExternalOauthView(ModelViewSet):
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = ExternalOauth.objects.all()
    serializer_class = ExternalOauthSerializer
    search_fields = ['user']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['user']


class TermCourseContentView(APIView):
    # permission_classes = [AllowAny]
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def post(self, request):
        user = request.data.get('user')
        course = request.data.get('course')
        term_service = TermCourseService(user, course)
        term_service.insert_student_context()
        return Response(data='插入成功')

    def get(self, request):
        user = request.query_params.get('user')
        course = request.query_params.get('course')
        term_course_id = request.query_params.get('term_course_id')
        term_service = TermCourseService(user, course)
        data = term_service.get_term_course_content(term_course_id)
        return Response(data=data)


class StudyReportView(APIView):
    # permission_classes = [AllowAny]
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def post(self, request):
        user = request.user.id
        course = request.data.get('course')
        term_service = TermCourseService(user, course)
        term_service.insert_student_context()
        return Response(data='插入成功')



