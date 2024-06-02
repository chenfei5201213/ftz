# 微信网页授权URL
import requests
from urllib.parse import urlencode

from django.core.cache import cache

# from server.settings import APPID
APPID = 'wxf1b19d71f836bb72'

WX_AUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"

# 微信换取用户信息和访问令牌的URL
WX_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WX_ACCESS_REFRESH_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/refresh_token"

# 微信换取用户信息的URL
WX_USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo"

# 设置授权回调URL
REDIRECT_URI = "http://www.ngsmq.online/api/us/wx/login/"


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
            "secret": '4e6c83dd0d8036d0e862bdc3af4ba9c4',
            "code": code,
            "grant_type": "authorization_code"
        }
        appid_ac_redis_key = f'ac:appid:{APPID}'
        data = cache.get(appid_ac_redis_key)
        if data is None:
            response = requests.get(WX_ACCESS_TOKEN_URL, params=params)
            data = response.json()
            if not data.get('errcode'):
                cache.set(appid_ac_redis_key, data, timeout=data.get('expires_in'))
        return data

    @staticmethod
    def refresh_token(refresh_token):
        params = {
            "appid": APPID,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        response = requests.get(WX_ACCESS_REFRESH_TOKEN_URL, params=params)
        data = response.json()

        return data

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
            "lang": "zh_CN",
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
        ac_redis_key = f'ac:appid:{self.appid}'
        data = cache.get(ac_redis_key)
        if data is None:
            response = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=params)
            access_token_data = response.json()
            data = access_token_data.get('access_token')
            if not access_token_data.get('errcode'):
                cache.set(ac_redis_key, data, timeout=access_token_data.get('expires_in'))
        return data


if __name__ == '__main__':
    wx = WechatUtil()
    # print(wx.get_user_info('81_YOahQcAeS-627hADZPMFSuztFZ_rsk4CYHuM6laETJ6BI8guSd59TFOTKvCQVFBZJu9qf6itgEpEN_40-bBRomlcw1LedXeJYXJfACdwjwo', 'o77756JY-IHm6zh-Ez3HVsLJIKvA'))
    print(wx.refresh_token('81_H5Z0wxr8i3yauI3jC2QrsNjxkRF1yJ0dUVYEqMoQwCVXYx3EF-VhmO1rTzIvfxSb_89hveTlOZw8I9z1lVJcohUQzVEutVH0T4dkF4j2oB0'))
