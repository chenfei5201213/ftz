from django.urls import path, include
from .views import AiVoiceViewSet


urlpatterns = [
    path('voice/', AiVoiceViewSet.as_view()),
]
