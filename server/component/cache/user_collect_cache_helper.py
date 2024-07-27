from django.core.cache import cache

from apps.user_center.models import ExternalUser
from component.cache import TIMEOUT, to_redis_key
from component.cache.enum_config import RedisKeyPrefixEnum

'''
用户收藏缓存类
'''


class UserCollectCacheHelper:
    def __init__(self, user: ExternalUser):
        self.user = user
        self.prefix = RedisKeyPrefixEnum.COLLECT.value[0]

    @property
    def material_collect_key(self):
        """素材收藏key, eg collect:ma:12345
        """
        return to_redis_key(self.prefix, RedisKeyPrefixEnum.MATERIAL.value[0], self.user.id)

    def set_material_collect_data(self, value):
        result = self.get_material_collect_data() or {}
        result.update({value: 1})
        return cache.set(self.material_collect_key, result)

    def get_material_collect_data(self, material_id: int = None):
        result = cache.get(self.material_collect_key) or {}
        if material_id:
            result = result.get(material_id)
        return result

    def delete_material_collect_data(self, material_id=None):
        result = cache.get(self.material_collect_key) or {}
        if material_id and result.get(material_id):
            del result[material_id]
        return cache.set(self.material_collect_key, result)

