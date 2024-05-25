from django.urls import path, include
from .views import UserLogin, WechatCallback


urlpatterns = [
    path('login/', UserLogin.as_view()),
    path('wx/callback/', WechatCallback.as_view()),
]
