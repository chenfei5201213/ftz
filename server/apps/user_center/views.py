import logging

from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.wechat_util import WechatUtil

logger = logging.getLogger('__name__')


# Create your views here.
class UserLogin(APIView):
    def get(self, request):
        redirect_url = WechatUtil.wechat_login()
        return Response(data={'redirect_url': redirect_url})


class WechatCallback(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        logger.info(f"code: ={code}")
        if not code:
            return HttpResponse("授权失败")
        access_token_data = WechatUser.access_token(code)
        logger.info(f"access_token_data: {access_token_data}")
        user_info = WechatUser.get_user_info(access_token_data['access_token'], access_token_data['openid'])
        logger.info(f"user_info: {user_info}")
        return Response(status=True)
