# src/apps/breaking/views.py

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from src.apps.breakes.models import Break
from src.api.breakes.serializers.serializers import BreakSerializers, BreakCreateSerializer
from src.apps.user.models import User,Roles


class BreakModelViewSet(ModelViewSet):
    queryset = Break.objects.all()
    serializer_class = BreakSerializers  # Default serializer

    def get_serializer_class(self):
        if self.action == 'create':
            return BreakCreateSerializer
        return BreakSerializers

    def perform_create(self, serializer):
        telegram_id = self.request.data.get('telegram_id')
        if not telegram_id:
            raise DRFValidationError({"telegram_id": "telegram_id majburiy."})

        user = User.objects.get(telegram_id=telegram_id)
        barber = Roles.objects.filter(user__roles__name='barber')

        serializer.save(barber=barber)
