from django.contrib.auth import get_user_model
from rest_framework import serializers
from src.apps.booking.models import Booking
from src.apps.breakes.models import Break
from src.apps.user.models import User
from django.utils import timezone

class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Break
        fields = ['id', 'start_time', 'end_time', 'barber', 'reason']

    def validate(self, data):
        user = data.get('barber') or getattr(self.instance, "barber", None)

        if not user:
            raise serializers.ValidationError("Barber user is required.")

        user_obj = user if isinstance(user, User) else User.objects.filter(pk=user).first()
        if not user_obj:
            raise serializers.ValidationError("Invalid user provided.")

        if not user_obj.roles.filter(name='Barber').exists():
            raise serializers.ValidationError("User must have Barber role to perform this action.")

        start_time = data.get('start_time') or getattr(self.instance, "start_time", None)
        end_time = data.get('end_time') or getattr(self.instance, "end_time", None)

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("start_time must be before end_time.")

        instance_id = self.instance.id if self.instance else None

        booking_overlap_qs = Booking.objects.filter(
            barber=user_obj,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if instance_id:
            booking_overlap_qs = booking_overlap_qs.exclude(id=instance_id)

        if booking_overlap_qs.exists():
            raise serializers.ValidationError("Break overlaps with existing bookings.")

        break_overlap_qs = Break.objects.filter(
            barber=user_obj,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if instance_id:
            break_overlap_qs = break_overlap_qs.exclude(id=instance_id)

        if break_overlap_qs.exists():
            raise serializers.ValidationError("Break overlaps with existing breaks.")

        if end_time and end_time < timezone.now():
            raise serializers.ValidationError("Break cannot end in the past.")

        return data


