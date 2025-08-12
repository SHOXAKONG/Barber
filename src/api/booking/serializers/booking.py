# from django.core.exceptions import ValidationError as DjangoValidationError
# from django.utils import timezone as dj_timezone
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError as DRFValidationError
# from .service import ServiceSerializer
# from src.apps.booking.models import Booking
# from src.apps.user.models import User


# class BookingSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField()
#     service = ServiceSerializer()
#     start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
#     end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

#     class Meta:
#         model = Booking
#         fields = ['id', 'user', 'service', 'start_time', 'end_time', 'status', 'notes']


# class BookingCreateSerializer(serializers.ModelSerializer):
#     telegram_id = serializers.IntegerField(write_only=True)
#     start_time = serializers.DateTimeField(input_formats=["%Y-%m-%d %H:%M"])

#     class Meta:
#         model = Booking
#         fields = ['telegram_id', 'notes', 'start_time', 'end_time', 'service']
#         read_only_fields = ['end_time']

#     def validate(self, data):
#         service = data.get('service')
#         start_time = data.get('start_time')

#         if not service or not start_time:
#             raise serializers.ValidationError("Service and start_time are required.")

#         if start_time < dj_timezone.now():
#             raise serializers.ValidationError("Cannot book in the past.")

#         duration = service.duration
#         end_time = start_time + dj_timezone.timedelta(minutes=duration)

#         overlapping_bookings = Booking.objects.filter(
#             start_time__lt=end_time,
#             end_time__gt=start_time,
#             status=Booking.BookingStatus.CONFIRMED
#         ).exists()

#         if overlapping_bookings:
#             raise serializers.ValidationError("This time slot is already booked.")

#         data['end_time'] = end_time
#         return data

#     def create(self, validated_data):
#         telegram_id = self.initial_data.get('telegram_id', None)

#         if not telegram_id:
#             raise serializers.ValidationError({"telegram_id": "telegram_id majburiy."})

#         user, _ = User.objects.get_or_create(telegram_id=telegram_id)
#         validated_data['user'] = user

#         try:
#             booking = Booking.objects.create(**validated_data)
#         except DjangoValidationError as e:
#             raise DRFValidationError(e.messages)

#         return booking