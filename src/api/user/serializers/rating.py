from rest_framework import serializers

from src.api.user.serializers import UserSerializer
from src.apps.user.models import Rating

class GetRatingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    barber = UserSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = [
            'id',
            "rating",
            'barber',
            'client'
        ]