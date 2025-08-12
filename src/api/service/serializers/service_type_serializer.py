from rest_framework import serializers
from src.apps.service.models import ServiceType

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'