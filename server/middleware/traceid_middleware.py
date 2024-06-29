# middleware.py
import logging
import uuid

from django.utils.deprecation import MiddlewareMixin


class TraceIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        trace_id = request.META.get('HTTP_TRACE_ID') or str(uuid.uuid4())  # 生成一个新的唯一的 trace ID
        request.META['TRACE_ID'] = trace_id  # 将 trace ID 存储在 request 的 META 中
        return None
