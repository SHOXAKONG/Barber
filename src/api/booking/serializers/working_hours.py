# from src.apps.booking.models import WorkingHours
# from rest_framework import serializers


from rest_framework import serializers
from src.apps.booking.models import WorkingHours

class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = '__all__'

# class WorkingHoursSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WorkingHours
#         fields = ['id', 'weekday', 'created_at', 'from_hour', 'to_hour', 'barber']
#         read_only_fields = ['id', 'barber']

#     def validate(self, data):
#         from_hour = data.get('from_hour')
#         to_hour = data.get('to_hour')
#         weekday = data.get('weekday')

#         if from_hour and to_hour and from_hour >= to_hour:
#             raise serializers.ValidationError({
#                 "to_hour": "Ishning tugash vaqti uning boshlanish vaqtidan keyin bo'lishi kerak."
#             })

#         barber = self.context['request'].user

#         existing_working_hours = WorkingHours.objects.filter(
#             barber=barber,
#             weekday=weekday
#         )
#         if self.instance:
#             existing_working_hours = existing_working_hours.exclude(pk=self.instance.pk)

#         if existing_working_hours.exists():
#             raise serializers.ValidationError(
#                 f"Ushbu sartarosh uchun bu kunga ({weekday}) ish vaqti allaqachon kiritilgan."
#             )

#         return data
