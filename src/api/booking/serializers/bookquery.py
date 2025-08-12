from rest_framework import serializers
from src.apps.user.models import User
from src.apps.service.models import Service

class BookingQuerySerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=["%Y-%m-%d"], required=True)
    barber_id = serializers.IntegerField(required=True)
    service_id = serializers.IntegerField(required=True)

    def validate_barber_id(self, value):
        user = User.objects.filter(id=value).first()
        if not user or not user.roles.filter('Barber'):
            raise serializers.ValidationError("Invalid barber_id.")
        return value

    def validate_service_id(self, value):
        if not Service.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid service_id.")
        return value
