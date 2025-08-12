from rest_framework import serializers
from src.apps.user.models import Roles

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'