# -*- coding: utf-8 -*-#
# filename: receive.py
import xml.etree.ElementTree as ET

from utils.wechat.wechat_enum import WechatMsgType, WechatEventType


def parse_xml(web_data):
    if len(web_data) == 0:
        return None
    xmlData = ET.fromstring(web_data)
    msg_type = xmlData.find('MsgType').text
    if msg_type == WechatMsgType.TEXT.value[0]:
        return TextMsg(xmlData)
    elif msg_type == WechatMsgType.IMAGE.value[0]:
        return ImageMsg(xmlData)
    elif msg_type == WechatMsgType.EVENT.value[0]:
        event = xmlData.find('Event').text
        if event == WechatEventType.CLICK.value[0]:
            return ClickMsg(xmlData)
        return EventMsg(xmlData)


class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


class TextMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Content = xmlData.find('Content').text.encode("utf-8")


class EventMsg(object):
    def __init__(self, xmlData):
        self.event = xmlData.find('Event').text
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text


class ClickMsg(EventMsg):
    def __init__(self, xmlData):
        EventMsg.__init__(self, xmlData)
        self.EventKey = xmlData.find('EventKey').text


class ImageMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text
