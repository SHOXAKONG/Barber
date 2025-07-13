from rest_framework import serializers
from src.apps.booking.models import Service
from decimal import Decimal


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'duration', 'price', 'contact']
        read_only_fields = ['id', 'name', 'description', 'contact']

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Xizmat davomiyligi musbat son bo'lishi kerak.")
        return value

    def validate_price(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Xizmat narxi musbat son bo'lishi kerak.")
        return value
