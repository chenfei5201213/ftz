from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.system.authentication import ExternalUserAuth
from apps.system.permission import ExternalUserPermission
from suntone_ise_cn_python.ai_voice import recognize_audio
from suntone_ise_cn_python.sample.exception import FileNotFoundException


# Create your views here.
class AiVoiceViewSet(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]
    def get(self, request):
        query_params = request.query_params
        file_path = query_params.get('file_path')
        ref_text = query_params.get('ref_text')
        try:
            result = recognize_audio(file_path, ref_text)
        except FileNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=result)

    @classmethod
    def get_extra_actions(cls):
        return {}
