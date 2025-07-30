# catalogue/middleware.py

import requests
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP
from django.conf import settings


API_KEY = settings.IPGEOLOCATION_API_KEY

def get_client_ip(request):

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Get the first IP in the list (the client's)
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

    # if request.META.get("HTTP_FAKE_IP"):
    #     return request.META["HTTP_FAKE_IP"]

    # x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    # if x_forwarded_for:
    #     return x_forwarded_for.split(",")[0].strip()

    # return request.META.get("REMOTE_ADDR")


def get_geolocation(ip):
    cache_key = f"geo_{ip}"
    if cached := cache.get(cache_key):
        return cached

    try:
        response = requests.get(
            f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip}",
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            result = {
                'country': data.get('country_name', ''),
                'city': data.get('city', '')
            }
            cache.set(cache_key, result, timeout=86400)  # 24 hours
            return result
    except Exception as e:
        print(f"Geo error: {e}")
    return {'country': '', 'city': ''}


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)

        # Block IP if blacklisted
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access denied")

        path = request.path
        geo = get_geolocation(ip)

        # Log the request
        RequestLog.objects.create(
            ip_address=ip,
            timestamp=now(),
            path=path,
            country=geo['country'],
            city=geo['city'],
        )

        response = self.get_response(request)
        return response
