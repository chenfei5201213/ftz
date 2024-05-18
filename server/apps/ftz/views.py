from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_extensions.cache.mixins import CacheResponseMixin


from .models import Course, Card, StudyMaterial, Lesson, Tag, EnumConfig, Survey, Question, UserResponse
from .serializers import CourseSerializer, CardListSerializer, StudyMaterialListSerializer, LessonListSerializer, \
    TagSerializer, StudyMaterialDetailSerializer, CardDetailSerializer, LessonDetailSerializer, EnumConfigSerializer, \
    SurveySerializer, QuestionSerializer, UserResponseSerializer


class CourseViewSet(CacheResponseMixin, ModelViewSet):
    """
    课程-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type']

    # def get_queryset(self):
    #     all = self.request.query_params.get('all', True)
    #     return Course.objects.get_queryset(all=all)


class LessonViewSet(CacheResponseMixin, ModelViewSet):
    """
    课时-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Lesson.objects.all()
    serializer_class = LessonListSerializer
    search_fields = ['title', 'version', 'course_id__title', 'group_name']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['course_id', 'type']

    def get_serializer_class(self):
        # 如果是根据ID查询详情，则使用详细查询序列化器
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return self.serializer_class


class CardViewSet(CacheResponseMixin, ModelViewSet):
    """
    卡片-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Card.objects.all()
    serializer_class = CardListSerializer
    search_fields = ['title', 'group_name', 'topic']
    ordering_fields = ['pk']
    ordering = ['pk']
    filterset_fields = ['type', 'difficulty']

    def get_serializer_class(self):
        # 如果是根据ID查询详情，则使用详细查询序列化器
        if self.action == 'retrieve':
            return CardDetailSerializer
        return self.serializer_class


class StudyMaterialViewSet(CacheResponseMixin, ModelViewSet):
    """
    学习素材-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialListSerializer
    search_fields = ['title']
    ordering_fields = ['pk']
    ordering = ['pk']
    filterset_fields = ['type']

    def get_serializer_class(self):
        # 如果是根据ID查询详情，则使用详细查询序列化器
        if self.action == 'retrieve':
            return StudyMaterialDetailSerializer
        return self.serializer_class


class TagViewSet(CacheResponseMixin, ModelViewSet):
    """
    标签-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ['name', 'value', 'module', 'service']
    ordering_fields = ['pk']
    ordering = ['pk']


class EnumConfigViewSet(CacheResponseMixin, ModelViewSet):
    """
    枚举配置-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = EnumConfig.objects.all()
    serializer_class = EnumConfigSerializer
    search_fields = ['name', 'module', 'service', 'value']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['module', 'service']


class SurveyViewSet(CacheResponseMixin, ModelViewSet):
    """
    问卷-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    search_fields = ['title', 'description']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    # filterset_fields = ['module', 'service']


class QuestionViewSet(CacheResponseMixin, ModelViewSet):
    """
    问卷题目-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    search_fields = ['question_text', 'question_type']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['question_type', 'survey']


class UserResponseViewSet(CacheResponseMixin, ModelViewSet):
    """
    问卷答复-增删改查
    """
    perms_map = {'get': '*', 'post': 'role_create',
                 'put': 'role_update', 'delete': 'role_delete'}
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer
    search_fields = ['user_id', 'question', 'answer']
    ordering_fields = ['pk']
    ordering = ['pk']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['user_id', 'survey', 'question']
