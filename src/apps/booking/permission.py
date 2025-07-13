from django.conf import settings
from rest_framework.permissions import BasePermission


class IsTrustedTelegramBot(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return False

        try:
            prefix, key = auth_header.split()
            if prefix.lower() != 'bearer':
                return False
        except ValueError:
            return False

        return key == settings.TELEGRAM_BOT_API_KEY
