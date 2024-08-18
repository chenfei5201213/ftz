from django.core.cache import cache

from apps.ftz.models import Course, Lesson
from apps.ftz.serializers import CourseSerializer
from component.cache import TIMEOUT, to_redis_key
from component.cache.enum_config import RedisKeyPrefixEnum


class CourseCacheHelper:
    """课程缓存类"""

    def __init__(self, course_id: int):
        self.course_id = course_id

    def course_key(self):
        return to_redis_key(RedisKeyPrefixEnum.COURSE.value[0], self.course_id)

    def set_course(self, data: dict):
        return cache.set(self.course_key(), data, timeout=TIMEOUT)

    def get_course(self):
        """查询缓存，不存在则查表，有数据的话写入缓存然后返回数据"""
        cacha_data = cache.get(self.course_key())
        if not cacha_data:
            data_obj = Course.objects.filter(id=self.course_id).first()
            if not data_obj:
                return
            cacha_data = CourseSerializer(data_obj).data
            self.set_course(cacha_data)
        return cacha_data

    def delete_course(self):
        cache.delete(self.course_key())
        cache.delete(self.course_material_count_key())

    def course_material_count_key(self):
        return to_redis_key(RedisKeyPrefixEnum.COURSE_MATERIAL_COUNT.value[0], self.course_id)

    def gen_course_material_count(self):
        count = 0
        lessons = Lesson.objects.filter(course_id=self.course_id).all()
        for lesson in lessons:
            for card in lesson.cards.all():
                count += len(card.study_materials.all())
        return count

    def set_course_material_count(self, data):
        cache.set(self.course_material_count_key(), data, timeout=TIMEOUT)

    def get_course_material_count(self):
        cache_data = cache.get(self.course_material_count_key())
        if not cache_data:
            cache_data = self.gen_course_material_count()
            self.set_course_material_count(cache_data)
        return cache_data
