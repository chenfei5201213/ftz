from django.core.cache import cache

from apps.ftz.models import Lesson
from apps.ftz.serializers import LessonDetailSerializer
from component.cache import TIMEOUT, to_redis_key
from component.cache.enum_config import RedisKeyPrefixEnum


class LessonCacheHelper:
    """课时缓存类"""

    def __init__(self, lesson_id: int):
        self.lesson_id = lesson_id

    def lesson_key(self):
        return to_redis_key(RedisKeyPrefixEnum.LESSON.value[0], self.lesson_id)

    def set_lesson(self, data: dict):
        return cache.set(self.lesson_key(), data, timeout=TIMEOUT)

    def get_lesson(self):
        """查询缓存，不存在则查表，有数据的话写入缓存然后返回数据"""
        cacha_data = cache.get(self.lesson_key())
        if not cacha_data:
            data_obj = Lesson.objects.filter(id=self.lesson_id).first()
            if not data_obj:
                return
            cacha_data = LessonDetailSerializer(data_obj).data
            self.set_lesson(cacha_data)
        return cacha_data

    def delete_lesson(self):
        cache.delete(self.lesson_key())
        cache.delete(self.lesson_material_count_key())

    def lesson_material_count_key(self):
        return to_redis_key(RedisKeyPrefixEnum.LESSON_MATERIAL_COUNT.value[0], self.lesson_id)

    def gen_lesson_material_count(self):
        count = 0
        lessons = Lesson.objects.filter(id=self.lesson_id).all()
        for lesson in lessons:
            for card in lesson.cards.all():
                count += len(card.study_materials.all())
        return count

    def set_lesson_material_count(self, data):
        cache.set(self.lesson_material_count_key(), data, timeout=TIMEOUT)

    def get_lesson_material_count(self):
        cache_data = cache.get(self.lesson_material_count_key())
        if not cache_data:
            cache_data = self.gen_lesson_material_count()
            self.set_lesson_material_count(cache_data)
        return cache_data
