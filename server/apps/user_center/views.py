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

from utils.custom_exception import FtzException
from utils.wechat_util import WechatUtil, WechatMiniUtil

from server import settings

from .models import ExternalUser, ExternalOauth
from .serializers import ExternalUserSerializer, ExternalOauthSerializer
from .service import TermCourseService, ExternalUserService
from ..ftz.serializers import TermCourseSerializer, CourseScheduleContentDetailSerializer
from ..mall.enum_config import StudyStatus
from ..mall.service import StudyContentService
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
    permission_classes = [AllowAny]
    authentication_classes = [ExternalUserAuth]
    # permission_classes = [ExternalUserPermission]

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
        user_id = request.user.id
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')
        study_material_id = request.data.get('study_material_id')
        study_status = request.data.get('study_status')
        study_duration = request.data.get('study_duration', 1)
        if study_status not in StudyStatus.__members__:
            return Response(f"study_status: {study_status} 不在{StudyStatus.__members__}中",
                            status=status.HTTP_400_BAD_REQUEST)
        term_service = TermCourseService(user_id, course_id)

        study_content = term_service.update_study_status(study_material_id, lesson_id,
                                                         StudyStatus[study_status].value[0], study_duration)
        if not study_content:
            return Response("学习内容不存在", status.HTTP_400_BAD_REQUEST)
        serializer = CourseScheduleContentDetailSerializer(study_content)
        return Response(data=serializer.data)


class MyCourseView(APIView):
    permission_classes = [AllowAny]
    # serializer_class = OrderSerializer
    """
    我的课程
    """

    def get(self, request, *args, **kwargs):
        """
        参数用户名，默认已支付的课程列表
        """
        try:
            user_id = request.query_params.get('user_id')
            study_service = StudyContentService(user_id)
            data = study_service.my_course()
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseLessonListView(APIView):
    permission_classes = [AllowAny]
    # serializer_class = OrderSerializer
    """
    课程对应的课时，不分页
    """

    def get(self, request, *args, **kwargs):
        """
        参数课程id
        """
        try:
            user_id = request.query_params.get('user_id')
            course_id = request.query_params.get('course_id')
            study_service = StudyContentService(user_id)
            data = study_service.course_lessons(course_id)
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseLessonDetailView(APIView):
    permission_classes = [AllowAny]
    # serializer_class = OrderSerializer
    """
    单个课时详情，包含卡片信息（需要处理课时释放逻辑）
    """

    def get(self, request, *args, **kwargs):
        """
        参数，课时id
        """
        try:
            user_id = request.query_params.get('user_id')
            course_id = request.query_params.get('course_id')
            lesson_id = request.query_params.get('lesson_id')
            study_service = StudyContentService(user_id)
            data = study_service.lesson_detail(course_id, lesson_id)
            return Response(data)
        except FtzException as e:
            logger.exception("异常：")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("异常：")
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudyMaterialView(APIView):
    permission_classes = [AllowAny]
    # serializer_class = OrderSerializer
    """
    单个课时详情，包含卡片信息（需要处理前一个学习了，后一个才能查看的问题）
    """

    def get(self, request, *args, **kwargs):
        """
        参数，课时id
        """
        try:
            user_id = request.query_params.get('user_id')
            course_id = request.query_params.get('course_id')
            card_id = request.query_params.get('card_id')
            study_service = StudyContentService(user_id)
            data = study_service.study_material_list(course_id, card_id)
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
