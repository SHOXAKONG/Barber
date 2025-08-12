from src.apps.user.models import User
from rest_framework import serializers
from src.apps.user.models import Roles

class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['telegram_id', 'phone_number', 'first_name', 'language']

    def validate_telegram_id(self, value):
        if User.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError("This user already exist")
        return value