from django.core.cache import cache

from apps.ftz.models import CourseScheduleContent
from component.cache import to_redis_key


class CourseScheduleContentCache:
    def __init__(self, course_id, lesson_id, ):
        self.r = cache
        self.course_id = course_id
        self.lesson_id = lesson_id
        self.lesson_cache_key = to_redis_key('csc', self.course_id, self.lesson_id)

    def add_course(self, study_material_id, study_material_info: dict):
        # sml 素材详情，课程+课时维度
        # sid 素材id
        study_material_cache_key = to_redis_key('sid', self.course_id, self.lesson_id, study_material_id)

        # 将课程内容存储为哈希
        self.r.hmset(study_material_cache_key, study_material_info)

        # 将课程ID添加到有序列表中，以保持顺序
        self.r.zadd(self.lesson_cache_key, {study_material_cache_key: self.study_material_id})

    def study_material_by_id(self, study_material_id):
        study_material_cache_key = to_redis_key('sid', self.course_id, self.lesson_id, study_material_id)

        course_data = self.r.hgetall(study_material_cache_key)
        return course_data

    def get_previous_course(self, study_material_id):
        # 获取当前课程ID在有序列表中的排名
        study_material_cache_key = to_redis_key('sid', self.course_id, self.lesson_id, study_material_id)

        rank = self.r.zrank(self.lesson_cache_key, study_material_cache_key)
        if rank is not None and rank > 0:
            # 获取前一个元素的键
            prev_course_key = self.r.zrange(self.lesson_cache_key, rank - 1, rank - 1)
            if prev_course_key:
                return self.study_material_by_id(int(prev_course_key[0].decode().split(':')[-1]))
        return None

    def get_next_course(self, study_material_id):
        # 获取当前课程ID在有序列表中的排名
        study_material_cache_key = to_redis_key('sid', self.course_id, self.lesson_id, study_material_id)

        rank = self.r.zrank(self.lesson_cache_key, study_material_cache_key)
        if rank is not None:
            # 获取后一个元素的键
            next_course_key = self.r.zrange(self.lesson_cache_key, rank + 1, rank + 1)
            if next_course_key:
                return self.study_material_by_id(int(next_course_key[0].decode().split(':')[-1]))
        return None
