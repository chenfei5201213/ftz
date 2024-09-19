from django.urls import path, include
from rest_framework import routers

from .study_record_view import StudyRecordTotalDurationView, StudyRecordTotalDaysView, StudyRecordCalendarView, \
    StudyRecordLuckyBagView
from .views import WechatLogin, WechatEchoStr, ExternalUserView, ExternalOauthView, TermCourseContentView, \
    WechatMiniLogin, UserLogin, WechatCallbackLogin, MyTokenRefreshView, StudyReportView, MyCourseView, \
    CourseLessonListView, CourseLessonDetailView, StudyMaterialDetailView, LearningProgressView, \
    FileViewSet, FreeCourse, StudyMaterialDetailQView, SurveyReportView, LogReportView, BatchLogReportView, \
    BatchSurveyReportView, UserHabitView, GenWechatSignature, TermCourseView, UserCollectView, UserCollectCheckView,\
    UserProfileView

router = routers.DefaultRouter()
router.register('user', ExternalUserView, basename='user')
router.register('auth', ExternalOauthView, basename='auth')
router.register('file', FileViewSet, basename='file')
urlpatterns = [
    path('', include(router.urls)),
    path('login/', UserLogin.as_view()),
    path('token/refresh/', MyTokenRefreshView.as_view()),
    path('login/gzh/', WechatLogin.as_view()),
    path('login/mini/', WechatMiniLogin.as_view()),
    path('wx/handle/', WechatEchoStr.as_view()),
    path('wx/login/', WechatCallbackLogin.as_view()),
    path('wx/signature/', GenWechatSignature.as_view()),
    path('term_course_content/', TermCourseContentView.as_view()),
    path('term_course/', TermCourseView.as_view()),
    path('study/report/', StudyReportView.as_view()),
    path('my/course/', MyCourseView.as_view(), name='my_course'),
    path('my/course/lesson/', CourseLessonListView.as_view(), name='my_course_lesson'),
    path('my/course/lesson/detail/', CourseLessonDetailView.as_view(), name='my_course_lesson_detail'),
    path('my/course/free/', FreeCourse.as_view(), name='free_course'),
    path('my/course/lesson/material_detail/', StudyMaterialDetailView.as_view(),
         name='my_course_lesson_material_detail'),
    path('my/course/lesson/material_detail_q/', StudyMaterialDetailQView.as_view(),
         name='my_course_lesson_material_detail'),
    path('my/course/learning_progress/', LearningProgressView.as_view(), name='my_course_learning_progress'),
    # path('wx/handle/', WechatEchoStr.as_view()),
    # 问卷
    path('survey/batch_report/', BatchSurveyReportView.as_view()),
    path('survey/report/', SurveyReportView.as_view()),
    # 埋点
    path('log/report/', LogReportView.as_view()),
    path('log/batch_report/', BatchLogReportView.as_view()),

    # 用户习惯
    path('habit/past/', UserHabitView.as_view()),

    # 用户收藏
    path('collect/', UserCollectView.as_view()),
    path('collect/check/', UserCollectCheckView.as_view()),

    # 数据分析
    path('stduy_record/total_duration/', StudyRecordTotalDurationView.as_view()),
    path('stduy_record/total_days/', StudyRecordTotalDaysView.as_view()),
    path('stduy_record/calendar/', StudyRecordCalendarView.as_view()),
    path('stduy_record/lucky_bag/', StudyRecordLuckyBagView.as_view()),

    # 个人中心
    path('user_center/user_profile/', UserProfileView.as_view()),

]
