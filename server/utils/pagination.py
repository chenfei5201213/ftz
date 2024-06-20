from urllib.parse import urlparse, urlunparse

from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ParseError

from server.settings import DOMAIN_NAME


class MyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('pageoff', None) or request.query_params.get('page', None) == '0':
            if queryset.count() < 800:
                return None
            raise ParseError('单次请求数据量大,请分页获取')
        return super().paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        # 修改 next 链接
        response.data['next'] = gen_nex_url(response.data['next'])
        return response


class PageOrNot:
    def paginate_queryset(self, queryset):
        if (self.paginator is None):
            return None
        elif self.request.query_params.get('pageoff', None) and queryset.count() < 500:
            return None
        elif self.request.query_params.get('pageoff', None) and queryset.count() >= 500:
            raise ParseError('单次请求数据量大,请求中止')
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


def gen_nex_url(old_url):
    if not old_url:
        return
    # 解析 URL
    parsed_url = urlparse(old_url)

    # 新的主机名
    new_hostname = DOMAIN_NAME

    # 替换主机名
    modified_url_components = (
        parsed_url.scheme, new_hostname, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment)

    # 重新构造 URL
    modified_url = urlunparse(modified_url_components)
    return modified_url
