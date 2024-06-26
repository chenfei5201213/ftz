from django.http import HttpResponseNotFound
from django.template import TemplateDoesNotExist


class TemplateNotFoundExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, TemplateDoesNotExist):
            return HttpResponseNotFound('<h1>Page not found</h1>')
        return None
