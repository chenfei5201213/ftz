from django.urls import path, include
from rest_framework import routers

from .views import CourseViewSet, LessonViewSet, CardViewSet, StudyMaterialViewSet, TagViewSet, EnumConfigViewSet, \
    MyTokenObtainPairView, OrderAdminViewSet
from .views import SurveyViewSet, QuestionViewSet, UserResponseViewSet, CourseScheduleViewSet
from .views import CourseScheduleStudentViewSet, UserStudyRecordViewSet, StudyMaterialSimpleViewSet
from .views import CardListSimpleViewSet, UserStudyContentViewSet, Test01View, QueryUserCourseInfo, RestUserCourse
from .views import AdminUserView, AdminUserTokenView, WechatMenuCreate, WechatMenuDelete

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
router.register('mall/order', OrderAdminViewSet, basename='study_content')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view()),
    path('test/01/', Test01View.as_view()),
    path('user/course_info/', QueryUserCourseInfo.as_view()),
    path('user/reset_course/', RestUserCourse.as_view()),
    path('admin/user/', AdminUserView.as_view()),
    path('admin/token/', AdminUserTokenView.as_view()),
    path('admin/wx/menu/create/', WechatMenuCreate.as_view()),
    path('admin/wx/menu/delete/', WechatMenuDelete.as_view()),

]
