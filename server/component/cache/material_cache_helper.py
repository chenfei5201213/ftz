from django.core.cache import cache

from component.cache import TIMEOUT


class MaterialCacheHelper:
    def __init__(self, material_id: int):
        self.material_id = material_id

    def material_detail_key(self):
        return f'material:d:{self.material_id}'

    def set_material_detail(self, data: dict):
        return cache.set(self.material_detail_key(), data, timeout=TIMEOUT)

    def get_material_detail(self):
        return cache.get(self.material_detail_key())
