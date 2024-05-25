# 微信网页授权URL
import requests
from urllib.parse import urlencode

from server.settings import APPID

WX_AUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"

# 微信换取用户信息和访问令牌的URL
WX_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"

# 微信换取用户信息的URL
WX_USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo"

# 设置授权回调URL
REDIRECT_URI = "http://www.ngsmq.online:8000/api/us/wx/callback/"


class WechatUtil:

    @staticmethod
    def wechat_login():
        """
        引导用户授权
        """
        params = {
            "appid": APPID,
            "response_type": "code",
            "scope": "snsapi_userinfo",
            "state": "STATE"
        }
        return WX_AUTH_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()]) + "&" + urlencode(
            {"redirect_uri": REDIRECT_URI})

    @staticmethod
    def access_token(code):
        params = {
            "appid": "your_app_id",
            "secret": "your_app_secret",
            "code": code,
            "grant_type": "authorization_code"
        }
        response = requests.get(WX_ACCESS_TOKEN_URL, params=params)
        access_token_data = response.json()
        return access_token_data

    @staticmethod
    def get_user_info(access_token, openid):
        # 换取用户信息
        user_info_params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        response = requests.get(WX_USER_INFO_URL, params=user_info_params)
        user_info = response.json()
        return user_info
