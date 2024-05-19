from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from suntone_ise_cn_python.ai_voice import recognize_audio


# Create your views here.
class AiVoiceViewSet(APIView):
    def get(self, request):
        query_params = request.query_params
        file_path = query_params.get('file_path')
        ref_text = query_params.get('ref_text')
        result = recognize_audio(file_path, ref_text)
        return Response(data=result)

    @classmethod
    def get_extra_actions(cls):
        return {}
