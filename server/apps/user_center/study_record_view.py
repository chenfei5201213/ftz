# encoding: utf-8
"""
@author: chenfei
@contact: chenfei@kuaishou.com
@software: PyCharm
@file: study_record_view.py
@time: 2024/9/8 15:44
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.system.authentication import ExternalUserAuth
from apps.system.permission import ExternalUserPermission
from apps.user_center.study_record_service import StudyRecordService
from component.cache.lesson_cache_helper import LessonCacheHelper
from utils.custom_exception import FtzException

logger = logging.getLogger('__name__')


class StudyRecordTotalDurationView(APIView):
    """
    学习总时长
    """
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def get(self, request, *args, **kwargs):
        """获取总学习时长"""
        try:
            user = request.user
            study_record_service = StudyRecordService(user)
            total_duration = study_record_service.get_study_total_duration()
            data = {
                'total_duration': total_duration
            }
            return Response(data)
        except FtzException as e:
            logger.exception(f'内部错误：')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'StudyRecordTotalDurationView')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudyRecordLuckyBagView(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def get(self, request, *args, **kwargs):
        """获取用户福袋"""
        try:
            user = request.user
            study_record_service = StudyRecordService(user)
            lesson_id = request.query_params.get('lesson_id')
            term_course_id = request.query_params.get('term_course_id')
            tab = request.query_params.get('tab')
            data = []
            if tab == 'finish':
                data = study_record_service.get_study_lucky_bag_finish(term_course_id, lesson_id)
            elif tab == 'collect':
                data = study_record_service.get_study_lucky_bag_collect(lesson_id)
            return Response(data)
        except FtzException as e:
            logger.exception(f'内部错误：')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'UserCollectCheckView')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudyRecordTotalDaysView(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def get(self, request, *args, **kwargs):
        """获取用户收藏记录"""
        try:
            user = request.user
            study_record_service = StudyRecordService(user)
            total_days = study_record_service.get_study_total_days()
            data = {
                'total_days': total_days
            }
            return Response(data)
        except FtzException as e:
            logger.exception(f'内部错误：')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'UserCollectCheckView')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudyRecordCalendarView(APIView):
    authentication_classes = [ExternalUserAuth]
    permission_classes = [ExternalUserPermission]

    def get(self, request, *args, **kwargs):
        """获取用户收藏记录"""
        try:
            user = request.user
            specific_year = request.query_params.get('year')
            specific_month = request.query_params.get('month')
            study_record_service = StudyRecordService(user)
            total_days = study_record_service.get_study_calendar(int(specific_year), int(specific_month))
            data = total_days
            return Response(data)
        except FtzException as e:
            logger.exception(f'内部错误：')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他异常并返回错误响应
            logger.exception(f'UserCollectCheckView')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
