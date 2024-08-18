from django.core.cache import cache

from apps.ftz.models import Card
from apps.ftz.serializers import CardDetailSimpleSerializer
from component.cache import TIMEOUT, to_redis_key
from component.cache.enum_config import RedisKeyPrefixEnum


class CardCacheHelper:
    """卡片缓存类"""

    def __init__(self, card_id: int):
        self.card_id = card_id

    def card_key(self):
        return to_redis_key(RedisKeyPrefixEnum.CARD.value[0], self.card_id)

    def set_card(self, data: dict):
        return cache.set(self.card_key(), data, timeout=TIMEOUT)

    def get_card(self):
        """查询缓存，不存在则查表，有数据的话写入缓存然后返回数据"""
        cacha_data = cache.get(self.card_key())
        if not cacha_data:
            data_obj = Card.objects.filter(id=self.card_id).first()
            if not data_obj:
                return
            cacha_data = CardDetailSimpleSerializer(data_obj).data
            self.set_card(cacha_data)
        return cacha_data

    def delete_card(self):
        cache.delete(self.card_key())
