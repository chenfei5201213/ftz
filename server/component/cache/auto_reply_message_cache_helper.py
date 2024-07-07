from django.core.cache import cache

from component.cache import to_redis_key


class AutoReplyMessageHelper:
    def __init__(self):
        self.keyword = 'auto_reply_message'

    @property
    def auto_reply_message_key(self):
        """"""
        return to_redis_key('au', self.keyword)

    def set_auto_reply_message(self, info: list):
        return cache.set(self.auto_reply_message_key, info, timeout=None)

    def get_auto_reply_message(self):
        return cache.get(self.auto_reply_message_key)

    @property
    def auto_replay_msg_subscribe_key(self):
        return to_redis_key('au', 'subscribe')

    def set_auto_replay_msg_subscribe(self, info: list):
        return cache.set(self.auto_replay_msg_subscribe_key, info, timeout=None)

    def get_auto_replay_msg_subscribe(self):
        return cache.get(self.auto_replay_msg_subscribe_key)
