# 微信网页授权URL
import requests
from urllib.parse import urlencode

from server.settings import APPID, MINIAPP_KEY

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
            "appid": APPID,
            "secret": MINIAPP_KEY,
            "code": code,
            "grant_type": "client_credential"
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


class WechatMiniUtil:
    """
    微信小程序
    """

    def __init__(self):
        self.appid = "wx8dc38edd7b81d08e"
        self.secret = "9d277900d826618a74dc35e323e14393"

    def login(self, code):
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": self.appid,
            "secret": self.secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data

    def get_user_info(self, access_token, openid):
        # 换取用户信息
        user_info_params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        response = requests.get('https://api.weixin.qq.com/cgi-bin/user/info', params=user_info_params)
        user_info = response.json()
        return user_info

    def access_token(self):
        params = {
            "appid": self.appid,
            "secret": self.secret,
            "grant_type": "client_credential"
        }
        ac_redis_key = f'ac:{self.appid}'
        data = cache.get(ac_redis_key)
        if data is None:
            response = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=params)
            access_token_data = response.json()
            data = access_token_data.get('access_token')
            cache.set(ac_redis_key, data, timeout=access_token_data.get('expires_in'))
        return data


if __name__ == '__main__':
    wx = WechatMiniUtil()
    print(wx.access_token())
