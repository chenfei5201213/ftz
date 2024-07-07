import random

from component.cache.auto_reply_message_cache_helper import AutoReplyMessageHelper
from utils.wechat import reply
from utils.wechat.keyword_match.keyword_match_factory import StringHandlerFactory
from utils.wechat.receive import TextMsg, EventMsg
from utils.wechat.reply import Msg
from utils.wechat.wechat_enum import WechatEventType


class WechatAutoReplyMessage:
    @staticmethod
    def text_msg_auto_pro(msg: TextMsg):
        content = msg.Content.decode('utf-8') if msg.Content else ""
        to_user = msg.FromUserName
        from_user = msg.ToUserName
        result = Msg().send()

        keyword_config = AutoReplyMessageHelper().get_auto_reply_message()
        if keyword_config:
            factory = StringHandlerFactory(keyword_config)
            processor = factory.get_processor()
            reply_content = processor.process_string(content)
            if reply_content:
                # 创建回复消息
                reply_msg = reply.TextMsg(to_user, from_user, reply_content)
                # 发送回复消息
                result = reply_msg.send()
        return result

    @staticmethod
    def event_auto_reply(msg: EventMsg):
        if msg.event == WechatEventType.SUBSCRIBE.value[0]:
            return WechatAutoReplyMessage.subscribe_auto_reply()
        return Msg().send()

    @staticmethod
    def subscribe_auto_reply(msg: EventMsg):
        to_user = msg.FromUserName
        from_user = msg.ToUserName
        result = Msg().send()

        keyword_config = AutoReplyMessageHelper().get_auto_replay_msg_subscribe()

        reply_content = random.choice(keyword_config)
        if reply_content:
            reply_msg = reply.TextMsg(to_user, from_user, reply_content.get('response'))
            # 发送回复消息
            result = reply_msg.send()
        return result
