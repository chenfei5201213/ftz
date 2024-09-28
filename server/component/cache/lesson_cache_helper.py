from django.core.cache import cache

from apps.ftz.models import Lesson, Card
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
        cache.delete(self.lesson_words_key())
        cache.delete(self.lesson_material_ids_key())

    def lesson_material_count_key(self):
        return to_redis_key(RedisKeyPrefixEnum.LESSON_MATERIAL_COUNT.value[0], self.lesson_id)

    def lesson_material_ids_key(self):
        return to_redis_key(RedisKeyPrefixEnum.LESSON_MATERIAL_IDS.value[0], self.lesson_id)

    def gen_lesson_material_count(self):
        count = 0
        lessons = Lesson.objects.filter(id=self.lesson_id).all()
        for lesson in lessons:
            for card in lesson.cards.all():
                count += len(card.study_materials.all())
        return count

    def gen_lesson_material_ids(self):
        ids = []
        lessons = Lesson.objects.filter(id=self.lesson_id).all()
        for lesson in lessons:
            for card in lesson.cards.all():
                ids.extend(card.study_materials.all().values_list('id', flat=True))
        return ids

    def set_lesson_material_count(self, data):
        cache.set(self.lesson_material_count_key(), data, timeout=TIMEOUT)

    def set_lesson_material_ids(self, data):
        cache.set(self.lesson_material_ids_key(), data, timeout=TIMEOUT)

    def get_lesson_material_count(self):
        cache_data = cache.get(self.lesson_material_count_key())
        if not cache_data:
            cache_data = self.gen_lesson_material_count()
            self.set_lesson_material_count(cache_data)
        return cache_data

    def get_lesson_material_ids(self):
        cache_data = cache.get(self.lesson_material_ids_key())
        if not cache_data:
            cache_data = self.gen_lesson_material_ids()
            self.set_lesson_material_ids(cache_data)
        return cache_data

    def lesson_words_key(self):
        return to_redis_key(RedisKeyPrefixEnum.LESSON_WORDS.value[0], self.lesson_id)

    def set_lesson_words(self):
        lesson = Lesson.objects.filter(id=self.lesson_id).first()
        if not lesson:
            return cache.set(self.lesson_words_key(), [], timeout=TIMEOUT)
        cards = Card.objects.filter(cards=lesson).values_list('words', flat=True)
        word_ids = [i for i in cards if i]
        return cache.set(self.lesson_words_key(), word_ids, timeout=TIMEOUT)

    def get_lesson_words(self):
        cache_data = cache.get(self.lesson_words_key())
        if cache_data is None:
            self.set_lesson_words()
            cache_data = cache.get(self.lesson_words_key())
        return cache_data




