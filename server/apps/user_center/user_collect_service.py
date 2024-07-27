
from apps.user_center.models import ExternalUser
from component.cache.user_collect_cache_helper import UserCollectCacheHelper


class UserCollectService:
    """
    用户收藏
    """
    def __init__(self, user: ExternalUser):
        self.user = user
        self.user_cache = UserCollectCacheHelper(self.user)

    def get_all(self):
        """获取所有收藏记录"""
        result = dict()
        result['material'] = self.get_material()
        return result

    def get_material(self, material_id=None):
        """获取收藏的素材"""
        result = self.user_cache.get_material_collect_data(material_id)
        return result
