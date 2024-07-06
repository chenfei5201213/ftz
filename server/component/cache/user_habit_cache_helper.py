from django.core.cache import cache

from apps.user_center.models import ExternalUser
from component.cache import TIMEOUT, to_redis_key

'''
用户习惯缓存类
'''


class UserHabitCacheHelper:
    def __init__(self, user: ExternalUser):
        self.user = user

    @property
    def user_survey_key(self):
        return to_redis_key('sur', self.user.id)

    def set_user_survey_data(self, value):
        return cache.set(self.user_survey_key, value)

    def get_user_survey_data(self):
        return cache.get(self.user_survey_key)

