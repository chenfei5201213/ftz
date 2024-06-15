from django.urls import path, include
from rest_framework import routers

from .views import CourseViewSet, LessonViewSet, CardViewSet, StudyMaterialViewSet, TagViewSet, EnumConfigViewSet, \
    MyTokenObtainPairView
from .views import SurveyViewSet, QuestionViewSet, UserResponseViewSet, CourseScheduleViewSet
from .views import CourseScheduleStudentViewSet, UserStudyRecordViewSet, StudyMaterialSimpleViewSet
from .views import CardListSimpleViewSet, UserStudyContentViewSet

router = routers.DefaultRouter()
router.register('course', CourseViewSet, basename='course')
router.register('lesson', LessonViewSet, basename='lesson')
router.register('card', CardViewSet, basename='card')
router.register('card_simple', CardListSimpleViewSet, basename='card')
router.register('material', StudyMaterialViewSet, basename='material')
router.register('material_simple', StudyMaterialSimpleViewSet, basename='material_simple')
router.register('tag', TagViewSet, basename='tag')
router.register('enum_config', EnumConfigViewSet, basename='enum')
router.register('survey/survey', SurveyViewSet, basename='survey')
router.register('survey/questions', QuestionViewSet, basename='questions')
router.register('survey/responses', UserResponseViewSet, basename='responses')
router.register('sc/course', CourseScheduleViewSet, basename='course')
router.register('sc/user', CourseScheduleStudentViewSet, basename='user')
router.register('sc/study_record', UserStudyRecordViewSet, basename='study_record')
router.register('sc/study_content', UserStudyContentViewSet, basename='study_content')
urlpatterns = [
    path('', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view()),
]
