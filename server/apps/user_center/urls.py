from django.urls import path, include
from rest_framework import routers
from .views import WechatLogin, WechatEchoStr, ExternalUserView, ExternalOauthView, TermCourseContentView, \
    WechatMiniLogin, UserLogin, WechatCallback

router = routers.DefaultRouter()
router.register('user', ExternalUserView, basename='user')
router.register('auth', ExternalOauthView, basename='auth')
urlpatterns = [
    path('', include(router.urls)),
    path('login/', UserLogin.as_view()),
    path('login/gzh/', WechatLogin.as_view()),
    path('login/mini/', WechatMiniLogin.as_view()),
    path('wx/handle/', WechatEchoStr.as_view()),
    path('wx/callback/', WechatCallback.as_view()),
    path('term_course_content/', TermCourseContentView.as_view()),
    # path('wx/handle/', WechatEchoStr.as_view()),
]
