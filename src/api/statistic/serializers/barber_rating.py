from rest_framework import serializers

class BarberRatingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    rating = serializers.FloatField()