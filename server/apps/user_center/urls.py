from django.urls import path, include
from rest_framework import routers
from .views import WechatLogin, WechatEchoStr, ExternalUserView, ExternalOauthView

router = routers.DefaultRouter()
router.register('user', ExternalUserView, basename='user')
router.register('auth', ExternalOauthView, basename='auth')
urlpatterns = [
    path('', include(router.urls)),
    path('login/', WechatLogin.as_view()),
    path('wx/handle/', WechatEchoStr.as_view()),
]
