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

    def material_study_progress_key(self, course_id, lesson_id):
        """学习进度key"""
        return f'material:sp:{course_id}:{lesson_id}:{self.material_id}:'

    def set_material_study_progress(self, data: dict, course_id, lesson_id):
        return cache.set(self.material_study_progress_key(course_id, lesson_id), data, timeout=TIMEOUT)

    def get_material_study_progress(self, course_id, lesson_id):
        return cache.get(self.material_study_progress_key(course_id, lesson_id))
