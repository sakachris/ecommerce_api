# catalogue/middleware.py

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.timezone import now

from .models import BlockedIP, RequestLog

API_KEY = settings.IPGEOLOCATION_API_KEY


def get_client_ip(request):
    """
    Extracts the client's IP address from the request.
    Handles both direct IP and forwarded IPs from proxies.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Get the first IP in the list (the client's)
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_geolocation(ip):
    """
    Fetches geolocation data for the given IP using the IP Geolocation API.
    Caches the result for 24 hours to reduce API calls.
    Returns a dictionary with 'country' and 'city'.
    """
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
    """
    Middleware to log requests and block blacklisted IPs.
    Logs the request's IP address, path, timestamp, country, and city.
    Blocks access for IPs that are in the BlockedIP model.
    """
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
