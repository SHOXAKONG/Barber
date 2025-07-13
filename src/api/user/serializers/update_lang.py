from src.apps.user.models import User
from rest_framework import serializers


class LanguageSerializer(serializers.ModelSerializer):
    user_lang = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['user_lang',]
