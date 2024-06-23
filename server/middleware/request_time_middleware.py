import time
import json
from apps.system.tasks import save_request_log
from django.utils.deprecation import MiddlewareMixin
from server.settings import REQUEST_LOG_SAMPLE_RATE

SAMPLE_RATE = int(REQUEST_LOG_SAMPLE_RATE or 100)  # Log 1 in every 100 requests


class RequestTimeMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.request_count = 0

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        self.request_count += 1
        if self.request_count % SAMPLE_RATE == 0:
            if hasattr(request, 'start_time'):
                request_end_time = time.time()
                duration = request_end_time - request.start_time

                # Collect request information
                method = request.method
                path = request.path
                remote_addr = request.META.get('REMOTE_ADDR', None)
                query_params = json.dumps(request.GET)
                body_params = json.dumps(request.POST)

                # Async save detailed request duration to database using Celery task
                save_request_log.delay(method, path, remote_addr, query_params, body_params, duration)

        return response
