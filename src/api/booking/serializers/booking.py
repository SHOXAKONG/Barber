from rest_framework import serializers
from src.apps.booking.models import Booking
from src.apps.service.models import Service

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "user",
            "barber",
            "service",
            "start_time",
            "notes",
        ]
        extra_kwargs = {
            "user": {"required": True},
            "barber": {"required": True},
            "service": {"required": True},
            "start_time": {"required": True},
        }

    def create(self, validated_data):
        service = validated_data["service"]
        validated_data["end_time"] = validated_data["start_time"] + service.duration

        booking = Booking(**validated_data)

        booking.full_clean()
        booking.save()
        return booking