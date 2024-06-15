import requests

from retrying import retry


def response_custom_retry(res):
    if res.status_code >= 500:
        return True
    else:
        return False


@retry(retry_on_result=response_custom_retry, wait_random_min=1000, wait_random_max=2000, stop_max_attempt_number=3)
def retry_request(method, url, *args, **kwargs):
    res = requests.request(method, url, *args, **kwargs)
    return res
