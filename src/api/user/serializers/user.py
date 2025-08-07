from rest_framework import serializers
from src.apps.user.models import User

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name', 'telegram_id', 'is_staff']