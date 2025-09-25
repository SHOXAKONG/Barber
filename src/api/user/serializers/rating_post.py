from rest_framework import serializers
from src.apps.user.models import Rating


class PostRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            'barber',
            'client',
            'rating'
        ]
