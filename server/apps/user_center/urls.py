from django.urls import path, include
from .views import WechatLogin, WechatEchoStr


urlpatterns = [
    path('login/', WechatLogin.as_view()),
    path('wx/handle/', WechatEchoStr.as_view())
]
