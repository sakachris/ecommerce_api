# catalogue/throttles.py
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler
from rest_framework.response import Response
from datetime import timedelta


def format_duration(seconds):
    return str(timedelta(seconds=int(seconds)))


class ResendVerificationThrottle(SimpleRateThrottle):
    scope = "resend_verification"

    def get_cache_key(self, request, view):
        # Throttle by user email or IP address (if unauthenticated)
        email = request.data.get("email")
        if not email:
            return self.get_ident(request)
        return f"throttle_resend_verification_{email.lower()}"

    def wait(self, request=None, view=None):
        """
        Override to provide custom wait time if throttled.
        Accepts request and view to regenerate cache key if not set.
        """
        cache_key = getattr(self, "_cache_key", None)
        if not cache_key and request and view:
            cache_key = self.get_cache_key(request, view)

        if not cache_key:
            return None

        history = self.cache.get(cache_key, [])
        if not history:
            return None

        now = self.timer()
        remaining_duration = self.duration - (now - history[-1])
        return max(remaining_duration, 0)


def custom_throttle_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        wait_time = getattr(exc, "wait", None)

        # If wait time is not already available from the exception
        if wait_time is None:
            view = context.get("view")
            request = context.get("request")
            if view and hasattr(view, "get_throttles"):
                for throttle in view.get_throttles():
                    if isinstance(throttle, ResendVerificationThrottle):
                        wait_time = throttle.wait(request=request, view=view)
                        break

        # Customize the throttle response
        retry_after_human = (
            format_duration(wait_time) if wait_time is not None else None
        )

        custom_detail = {
            "detail": "Too many resend attempts. Please try again later.",
            "available_in_seconds": int(wait_time) if wait_time is not None else None,
            "retry_after": retry_after_human,
        }

        response.data = custom_detail
        response.status_code = 429
        if wait_time is not None:
            response["Retry-After"] = str(int(wait_time))

    return response
