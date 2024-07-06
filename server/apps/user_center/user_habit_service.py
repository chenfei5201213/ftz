from apps.user_center.models import ExternalUser
from component.cache.user_habit_cache_helper import UserHabitCacheHelper


class UserHabitService:
    def __init__(self, user: ExternalUser):
        self.user = user
        self.user_habit_cache = UserHabitCacheHelper(self.user)

    def get_all(self):
        result = dict()
        result['survey'] = self.get_user_survey
        return result

    @property
    def get_user_survey(self):
        return self.user_habit_cache.get_user_survey_data()
