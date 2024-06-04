from django.urls import path, include
from rest_framework import routers
from .views import WechatLogin, WechatEchoStr, ExternalUserView, ExternalOauthView, TermCourseContentView, \
    WechatMiniLogin, UserLogin, WechatCallbackLogin, MyTokenRefreshView, StudyReportView, MyCourseView, \
    CourseLessonListView, CourseLessonDetailView, StudyMaterialView,StudyMaterialDetailView,LearningProgressView

router = routers.DefaultRouter()
router.register('user', ExternalUserView, basename='user')
router.register('auth', ExternalOauthView, basename='auth')
urlpatterns = [
    path('', include(router.urls)),
    path('login/', UserLogin.as_view()),
    path('token/refresh/', MyTokenRefreshView.as_view()),
    path('login/gzh/', WechatLogin.as_view()),
    path('login/mini/', WechatMiniLogin.as_view()),
    path('wx/handle/', WechatEchoStr.as_view()),
    path('wx/login/', WechatCallbackLogin.as_view()),
    path('term_course_content/', TermCourseContentView.as_view()),
    path('study/report/', StudyReportView.as_view()),
    path('my/course/', MyCourseView.as_view(), name='my_course'),
    path('my/course/lesson/', CourseLessonListView.as_view(), name='my_course_lesson'),
    path('my/course/lesson/detail/', CourseLessonDetailView.as_view(), name='my_course_lesson_detail'),
    path('my/course/lesson/material/', StudyMaterialView.as_view(), name='my_course_lesson_material'),
    path('my/course/lesson/material_detail/', StudyMaterialDetailView.as_view(), name='my_course_lesson_material_detail'),
    path('my/course/learning_progress/', LearningProgressView.as_view(), name='my_course_learning_progress'),
    # path('wx/handle/', WechatEchoStr.as_view()),
]
