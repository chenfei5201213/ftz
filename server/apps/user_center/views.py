import hashlib
import logging

from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.wechat_util import WechatUtil

from server import settings

logger = logging.getLogger('__name__')


# Create your views here.
class UserLogin(APIView):
    def get(self, request):
        redirect_url = WechatUtil.wechat_login()
        return Response(data={'redirect_url': redirect_url})


class WechatLogin(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        logger.info(f"code: ={code}")
        if not code:
            return Response("授权失败", status=400)
        access_token_data = WechatUtil.access_token(code)
        if access_token_data:
            return Response(data=access_token_data)
        logger.info(f"access_token_data: {access_token_data}")
        user_info = WechatUtil.get_user_info(access_token_data['access_token'], access_token_data['openid'])
        logger.info(f"user_info: {user_info}")
        return Response(data=user_info)


class WechatEchoStr(APIView):
    def get(self, request):
        try:
            data = request.query_params
            signature = data.get('signature')
            timestamp = data.get('timestamp')
            nonce = data.get('nonce')
            echostr = data.get('echostr')
            token = settings.WECHAT_TOKEN  # 从 Django 设置中获取 Token

            # 验证消息的确来自微信服务器
            list_ = [token, timestamp, nonce]
            list_.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list_)
            hashcode = sha1.hexdigest()

            if hashcode == signature:
                return Response(echostr)
            else:
                return Response('验证失败', status=400)  # 返回 400 错误
        except Exception as e:
            return Response({"error": str(e)}, status=500)  # 返回 500 错误
