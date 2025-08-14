from rest_framework import serializers
from src.apps.service.models import ServiceType
from .service_serializer import ServiceSerializer

class ServiceTypeSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'services', 'barber']

class ServiceTypeOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'barber']