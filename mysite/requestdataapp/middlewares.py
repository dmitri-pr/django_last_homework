from django.http import HttpRequest
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = self.get_client_ip(request)
        min_interval = 0
        cache_key = f'last_request_time_{ip_address}'
        last_request_time = cache.get(cache_key)
        current_time = timezone.now()

        if last_request_time is None:
            cache.set(cache_key, current_time, timeout=None)
        else:
            time_since_last_request = (current_time - last_request_time).total_seconds()
            if time_since_last_request < min_interval:
                return HttpResponseForbidden(
                    '<br><br>Too many requests. Please wait before trying again.'
                )
            else:
                cache.set(cache_key, current_time, timeout=None)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def set_useragent_on_request_middleware(get_response):
    print('initial call')

    def middleware(request: HttpRequest):
        print('before getting response')
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print('after getting response')
        return response

    return middleware

