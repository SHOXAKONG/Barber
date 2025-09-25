import time
from django.http import JsonResponse
from src.apps.common.utils.logger import log_action

class AntiBotMiddleware:
    RATE_LIMIT = 60       # max requests
    TIME_WINDOW = 60      # seconds
    VISITORS = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        now = time.time()

        if ip not in self.VISITORS:
            self.VISITORS[ip] = []
        self.VISITORS[ip] = [t for t in self.VISITORS[ip] if now - t < self.TIME_WINDOW]
        self.VISITORS[ip].append(now)

        if len(self.VISITORS[ip]) > self.RATE_LIMIT:
            return JsonResponse(
                {"detail": "Too many requests, try again later."}, status=429
            )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class ActionLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            user = request.user if hasattr(request, "user") else None
            ip = request.META.get("REMOTE_ADDR") or request.META.get("HTTP_X_FORWARDED_FOR")
            action = f"{request.method} {request.path} {response.status_code}"
            if getattr(user, "is_authenticated", False):
                log_action(user, action, ip=ip)
        except Exception:
            pass

        return response
