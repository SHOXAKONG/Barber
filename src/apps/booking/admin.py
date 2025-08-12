from django.contrib import admin
from .models import WorkingHours, Booking

@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('weekday', 'from_hour', 'to_hour', 'barber')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'status', 'notes', 'cancel_reason')