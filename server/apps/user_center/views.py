import hashlib
import logging

from django.core.cache import cache
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
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
from .service import ExternalUserService
from ..ftz.models import CourseScheduleContent
from ..ftz.serializers import TermCourseSerializer, CourseScheduleContentDetailSerializer
from ..ftz.service import TermCourseService
from ..mall.enum_config import StudyStatus
from .service import StudyContentService
from ..system.authentication import ExternalUserTokenObtainPairSerializer, ExternalUserAuth
from ..system.models import File, User
from ..system.permission import ExternalUserPermission
from ..system.serializers import FileSerializer

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
    """小程序登录接口"""
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        logger.info(f"code: ={code}")
        code_token_redis_key = f'tk:code:{code}'
        cache_data = cache.get(code_token_redis_key)
        if cache_data:
            return Response(data=cache_data)
        if not code:
            return Response("授权失败", status=400)
        wx = WechatMiniUtil()
        user_info = wx.login(code)

        if not user_info:
            return Response("获取用户信息失败", status=400)
        user_info['mini_openid'] = user_info.pop('openid')
        user_service = ExternalUserService(user_info['unionid'])
        _user = user_service.get_user()
        if not _user:
            _user = user_service.save(user_info)
        else:
            _user.mini_openid = user_info.get('mini_openid')
            _user.save()
        token_result = gen_token(_user, code, user_info['unionid'])
        serializer = ExternalUserSerializer(_user)
        data = {"user": serializer.data}
        data.update(token_result)
        return Response(data)


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
        if not user_info:
            return Response("获取用户信息失败", status=400)
        user_service = ExternalUserService(user_info['unionid'])
        _user = user_service.get_user()
        if not _user:
            _user = user_service.save(user_info)
        else:
            _user.openid = user_info.get('openid')
            _user.save()
        logger.info(f"code: {code}, user_info:{user_info}")
        token_result = gen_token(_user, code, user_info["unionid"])

        serializer = ExternalUserSerializer(_user)
        data = {"user": serializer.data}
        data.update(token_result)
        return Response(data)


def gen_token(user: ExternalUser, code, unionid):
    tk_code_key = f'tk:code:{code}'
    tk_unionid_key = f'tk:unionid:{unionid}'
    logger.info(f"unionid:{unionid}, code:{code}")
    token_result = cache.get(tk_unionid_key)
    if not token_result:
        token = ExternalUserTokenObtainPairSerializer.get_token(user)
        token_result = {'access': str(token.access_token), 'refresh': str(token)}
        cache.set(tk_code_key, token_result, timeout=7200)
        cache.set(tk_unionid_key, token_result, timeout=7200)
    return token_result


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
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def post(self, request):
        user = request.user.id
        course = request.data.get('course')
        term_service = TermCourseService(user, course)
        term_service.insert_student_context()
        return Response(data='插入成功')

    def get(self, request):
        user = request.user.id
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
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    """
    我的课程
    """

    def get(self, request, *args, **kwargs):
        """
        参数用户名，默认已支付的课程列表
        """
        try:
            user_id = request.user.id
            study_service = StudyContentService(user_id)
            data = study_service.my_course()
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseLessonListView(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    """
    课程对应的课时，不分页
    """

    def get(self, request, *args, **kwargs):
        """
        参数课程id
        """
        try:
            user_id = request.user.id
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
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    """
    单个课时详情，包含卡片信息（需要处理课时释放逻辑）
    """

    def get(self, request, *args, **kwargs):
        """
        参数，课时id
        """
        try:
            user_id = request.user.id
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


class StudyMaterialDetailView(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    """
    单个素材详情
    """

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            lesson_id = request.query_params.get('lesson_id')
            study_material_id = request.query_params.get('study_material_id')
            study_content = CourseScheduleContent.objects.filter(user=user_id, lesson=lesson_id,
                                                                 study_material=study_material_id).first()
            study_content_info = CourseScheduleContentDetailSerializer(study_content).data
            study_service = StudyContentService(user_id)
            card = study_service.card_study_progress(study_content.card, study_content.lesson)
            study_content_info['card'] = card
            return Response(study_content_info)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'查询课时详情异常：')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LearningProgressView(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    """
    学习进度
    """

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            course_id = request.query_params.get('course_id')
            card_id = request.query_params.get('card_id')
            study_service = StudyContentService(user_id)
            data = study_service.learning_progress(course_id)
            return Response(data)
        except FtzException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'学习进度未知异常')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    文件上传用
    """
    perms_map = None
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    parser_classes = [MultiPartParser, JSONParser]
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filterset_fields = ['type']
    search_fields = ['name']
    ordering = ['-create_time']

    def perform_create(self, serializer):
        fileobj = self.request.data.get('file')
        name = fileobj._name
        size = fileobj.size
        mime = fileobj.content_type
        type = '其它'
        if 'image' in mime:
            type = '图片'
        elif 'video' in mime:
            type = '视频'
        elif 'audio' in mime:
            type = '音频'
        elif 'application' or 'text' in mime:
            type = '文档'

        user = User.objects.first()
        instance = serializer.save(create_by=user, name=name, size=size, type=type, mime=mime)
        instance.path = settings.MEDIA_URL + instance.file.name
        instance.save()


class FreeCourse(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def post(self, request, *args, **kwargs):
        """免费课程领取"""
        try:
            user = request.user
            free_product_id = request.data.get('free_product_id')
            study_service = StudyContentService(user.id)
            data = study_service.receive_free_product(free_product_id)
            return Response(data)
        except FtzException as e:
            logger.exception(f'内部错误：')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'领取课程异常')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)