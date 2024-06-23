from django.utils import timezone
import time


class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()  # 记录请求开始时间
        response = self.get_response(request)
        request.end_time = time.time()  # 记录请求结束时间

        # 计算请求耗时
        duration = request.end_time - request.start_time
        response["X-Response-Time"] = f"{duration:.6f}"  # 将耗时添加到响应头中，单位为秒

        return response
