# 微信网页授权URL
import logging
import os
import time

from django.utils import timezone

from server.settings import REDIRECT_URI, BUY_FINISH_URL
from utils.wechat.template_message_config import COURSE_REGISTRATION_SUCCESS_NOTIFICATION, CLASS_REMINDER_MESSAGE

os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from urllib.parse import urlencode

from django.core.cache import cache

from utils.custom_exception import WxException, ErrorCode
from utils.retry_requests import retry_request

from utils.wechat import APPID, WX_AUTH_URL, SECRET, WX_CODE_ACCESS_TOKEN_URL, \
    WX_CODE_ACCESS_REFRESH_TOKEN_URL, \
    WX_USER_INFO_URL, WX_ACCESS_TOKEN_URL, WX_TEMPLATE_MESSAGE_SEND_URL, WX_TICKET_URI, WX_MENU_GET_URL, \
    WX_MENU_CREATE_URL, WX_MENU_DELETE_URL

logger = logging.getLogger(__name__)


class WechatBase:
    def __init__(self):
        self.appid = APPID

    def request(self, method, url, *args, **kwargs):
        res = retry_request(method, url, *args, **kwargs)
        logger.info(f"method={method},url={url}, args={args}, kwargs={kwargs} ")
        if res.status_code == 200:
            return res.json()
        logger.error(f"status_code:{res.status_code}, result: {res.content}")
        return False

    @property
    def access_token_redis_key(self):
        return f"wx:tc:{self.appid}"

    def get_access_token(self):
        access_token_data = cache.get(self.access_token_redis_key)
        if not access_token_data or int(
                time.time() > access_token_data.get('init_time', 0) + access_token_data['expires_in'] + 10):
            params = {
                'grant_type': 'client_credential',
                'appid': self.appid,
                'secret': SECRET
            }
            access_token_data = self.request(method='get', url=WX_ACCESS_TOKEN_URL, params=params)
            if not access_token_data.get('errcode'):
                access_token_data['init_time'] = int(time.time())
                cache.set(self.access_token_redis_key, access_token_data, timeout=access_token_data.get('expires_in'))
            else:
                raise WxException(f"获取token异常：{access_token_data.get('errcode')}",
                                  ErrorCode.WxGzhInterFaceException.value)
        return access_token_data


class WechatUtil(WechatBase):
    """公众号"""

    def wechat_login(self):
        """
        引导用户授权
        """
        params = {
            "appid": self.appid,
            "response_type": "code",
            "scope": "snsapi_userinfo",
            "state": "STATE"
        }
        return WX_AUTH_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()]) + "&" + urlencode(
            {"redirect_uri": REDIRECT_URI})

    def access_token(self, code):
        params = {
            "appid": self.appid,
            "secret": SECRET,
            "code": code,
            "grant_type": "authorization_code"
        }
        appid_ac_redis_key = f'ac:appid:{APPID}:code:{code}'
        access_token_data = cache.get(appid_ac_redis_key)
        if access_token_data is None:
            access_token_data = self.request(method='get', url=WX_CODE_ACCESS_TOKEN_URL, params=params)
            if not access_token_data.get('errcode'):
                cache.set(appid_ac_redis_key, access_token_data, timeout=access_token_data.get('expires_in'))
        return access_token_data

    def refresh_token(self, refresh_token):
        params = {
            "appid": self.appid,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        response = self.request(method='get', url=WX_CODE_ACCESS_REFRESH_TOKEN_URL, params=params)
        return response

    def get_user_info(self, access_token, openid):
        # 换取用户信息
        user_info_params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        user_info = self.request(method='get', url=WX_USER_INFO_URL, params=user_info_params)
        return user_info

    def get_jsapi_ticket(self):
        params = {
            "access_token": self.get_access_token(),
            "type": "jsapi"
        }
        # response = requests.get(url, params=params)
        response = self.request(method='get', url=WX_TICKET_URI, params=params)
        return response.get("ticket")


class WechatTemplateMessage(WechatBase):
    def send_bug_course_success_message(self, openid, product_info: dict, order_id: int):
        body = COURSE_REGISTRATION_SUCCESS_NOTIFICATION
        course_info = product_info.get('course_info', {})
        term_courses = product_info.get('term_courses', {})
        body['touser'] = openid
        body['url'] = BUY_FINISH_URL + str(order_id)
        body['data']['thing1']['value'] = course_info.get('title')
        body['data']['time7']['value'] = term_courses.get('course_start')
        params = {
            'access_token': self.get_access_token().get("access_token")
        }
        result = self.request(method='post', url=WX_TEMPLATE_MESSAGE_SEND_URL, params=params, json=body)
        return result

    def send_class_reminder(self, openid, course_info: dict):
        body = CLASS_REMINDER_MESSAGE
        body['touser'] = openid
        body['url'] = ''  # todo 待补充 加老师页面链接
        body['data']['thing1']['value'] = course_info.get('title')
        body['data']['time2']['value'] = course_info.get('open_time')
        params = {
            'access_token': self.get_access_token().get("access_token")
        }
        result = self.request(method='post', url=WX_TEMPLATE_MESSAGE_SEND_URL, params=params, json=body)
        return result


class WechatMenu(WechatBase):

    def get_current_menu(self):
        params = {
            'access_token': self.get_access_token().get("access_token")
        }
        result = self.request(method='get', url=WX_MENU_GET_URL, params=params)
        return result

    def create_menu(self, menu_data):
        """
        https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Creating_Custom-Defined_Menu.html
        """
        params = {
            'access_token': self.get_access_token().get("access_token")
        }
        result = self.request(method='post', url=WX_MENU_CREATE_URL, params=params, json=menu_data)
        return result

    def delete_menu(self, menu_data):
        """
        """
        params = {
            'access_token': self.get_access_token().get("access_token")
        }
        result = self.request(method='get', url=WX_MENU_DELETE_URL, params=params, json=menu_data)
        return result


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
        data = self.request(method='get', url=url, params=params)
        # response = requests.get(url, params=params)
        # data = response.json()
        # logger.info(f'code: {data}')
        return data

    def get_user_info(self, access_token, openid):
        # 换取用户信息
        user_info_params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN",
        }
        url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        user_info = self.request(method='get', url='', user_info_params=user_info_params)
        # response = requests.get('https://api.weixin.qq.com/cgi-bin/user/info', params=user_info_params)
        # user_info = response.json()

        return user_info

    def access_token(self):
        params = {
            "appid": self.appid,
            "secret": self.secret,
            "grant_type": "client_credential",

        }
        url = 'https://api.weixin.qq.com/cgi-bin/token'
        ac_redis_key = f'ac:appid:{self.appid}'
        access_token = cache.get(ac_redis_key)

        if access_token is None:
            access_token_data = self.request(method='get', url=url, params=params)
            # response = requests.get(url, params=params)
            # access_token_data = response.json()  # {'access_token': '81__wVcqpTV29-gJVpdLn81L_1BqjiDUp9ovdyLd14P9TXzR0C5_6hjxcmqK-DdNe7qpfx5Dvnxovgh-xfiLMI7Pvx_jQ5pYilT-wf9uBAgYKgrf10UK-kLvP3h7usVYRgAGAPSL','expires_in': 7200}
            access_token = access_token_data.get('access_token')
            if not access_token_data.get('errcode'):
                cache.set(ac_redis_key, access_token, timeout=access_token_data.get('expires_in'))
        return access_token

    def get_phone_number(self, access_token, code, openid):
        params = {
            "access_token": access_token
        }
        body = {
            "code": code,
            "openid": openid
        }
        url = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber'
        response = self.request(method='post', url=url, json=body, params=params)
        return response

    def request(self, method, url, *args, **kwargs):
        res = retry_request(method, url, *args, **kwargs)
        logger.info(f"method={method},url={url}, args={args}, kwargs={kwargs} ")
        if res.status_code == 200:
            return res.json()
        logger.error(f"status_code:{res.status_code}, result: {res.content}")
        return False


if __name__ == '__main__':
    # wx = WechatUtil()
    # # print(wx.get_user_info('81_YOahQcAeS-627hADZPMFSuztFZ_rsk4CYHuM6laETJ6BI8guSd59TFOTKvCQVFBZJu9qf6itgEpEN_40-bBRomlcw1LedXeJYXJfACdwjwo', 'o77756JY-IHm6zh-Ez3HVsLJIKvA'))
    # print(wx.refresh_token('81_H5Z0wxr8i3yauI3jC2QrsNjxkRF1yJ0dUVYEqMoQwCVXYx3EF-VhmO1rTzIvfxSb_89hveTlOZw8I9z1lVJcohUQzVEutVH0T4dkF4j2oB0'))
    # xcx = WechatMiniUtil()
    # r = xcx.login()
    # ac = '81_rFx_WTg1Nd6weUu5RkQOvp34PPbrgxBTLVMB0rxKrKO03pxEZ38EOib1Acdf6lYtIZUOsYe669fhfr7fHrPDMDQ0R77zRIA0rleIIKe20LpjmRBbL7Nt5Z_MtN4XGTjAGADMZ'
    # userid = 'o0Dq76zXxM6v0dFJJRTcF302NyTs'
    # code = '0e1dz5100MYFgS1Go9100dOXdC4dz51J'
    # xcx.get_phone_number(ac, code, userid)
    # wx = WechatTemplateMessage()
    # token = wx.send_class_reminder('o77756JY-IHm6zh-Ez3HVsLJIKvA',
    #                                {"title": "测试课程", 'open_time': timezone.localtime().strftime("%Y年%m月%d日")})
    # print(token)
    wx = WechatMenu()
    r = wx.get_current_menu()
    print(r)
