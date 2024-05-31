import hashlib
import logging
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from utils.wechat_util import WechatUtil, WechatMiniUtil

from server import settings

from .models import ExternalUser, ExternalOauth
from .serializers import ExternalUserSerializer, ExternalOauthSerializer
from .service import TermCourseService
from ..ftz.serializers import TermCourseSerializer

logger = logging.getLogger('__name__')


# Create your views here.
class UserLogin(APIView):

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
        if not code:
            return Response("授权失败", status=400)
        wx = WechatMiniUtil()
        data = wx.login(code)
        # if access_token_data:
        #     return Response(data=access_token_data)
        # logger.info(f"access_token_data: {access_token_data}")
        # user_info = WechatUtil.get_user_info(access_token_data['access_token'], access_token_data['openid'])
        # logger.info(f"user_info: {user_info}")
        return Response(data=data)


class WechatCallback(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    queryset = ExternalUser.objects.all()
    serializer_class = ExternalUserSerializer

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
        data = {
            'openid': access_token_data['openid'],
            'nickname': user_info.get('nickname'),
        }
        serializer_class = self.get_serializer_class()
        serializer = serializer_class()
        serializer.save(**data)
        return Response(serializer.data)


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
    permission_classes = [AllowAny]

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
