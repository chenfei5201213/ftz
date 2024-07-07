from enum import Enum


class WechatMsgType(Enum):
    EVENT = ('event', '点击事件')
    TEXT = ('text', '文本消息')
    IMAGE = ('image', '图片消息')
    VOICE = ('voice', '语音消息')
    LOCATION = ('location', '地理位置消息')
    LINK = ('link', '链接消息')


class WechatEventType(Enum):
    SUBSCRIBE = ('subscribe', '订阅')
    UNSUBSCRIBE = ('unsubscribe', '取消订阅')





