from rest_framework import serializers
from src.apps.user.models import User

class UserSerializer(serializers.ModelSerializer):
    total_bookings = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id',
                  'telegram_id',
                  'first_name',
                  'phone_number',
                  'language',
                  'photo',
                  'description',
                  'rating',
                  'default_from_hour',
                  'default_to_hour',
                  'roles',
                  'total_bookings']
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
                  'first_name',
                  'phone_number',
                  'language',
                  'photo',
                  'description',
                  'default_from_hour',
                  'default_to_hour']