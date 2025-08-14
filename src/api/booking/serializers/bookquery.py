from rest_framework import serializers
from datetime import datetime
from src.apps.user.models import User
from src.apps.service.models import Service
from src.apps.booking.models import WorkingHours

class BookingQuerySerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=["%Y-%m-%d"], required=True)
    barber_id = serializers.IntegerField(required=True)
    service_id = serializers.IntegerField(required=True)

    def validate_barber_id(self, value):
        user = User.objects.filter(id=value).first()
        if not user or not user.roles.filter(name='Barber').exists():
            raise serializers.ValidationError("Invalid barber_id: must be a valid barber.")
        return value

    def validate_service_id(self, value):
        if not Service.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid service_id: service does not exist.")
        return value

    def validate_date(self, value):
        if value < datetime.today().date():
            raise serializers.ValidationError("Date cannot be in the past.")
        return value

    def validate(self, attrs):
        barber_id = attrs.get('barber_id')
        date = attrs.get('date')

        if barber_id and date:
            has_hours = WorkingHours.objects.filter(
                barber_id=barber_id,
                weekday=date.weekday()
            ).exists()
            if not has_hours:
                raise serializers.ValidationError(
                    "The barber has no working hours on this day."
                )
        return attrs