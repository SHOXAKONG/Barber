from django.contrib import admin
from .models import Service, WorkingHours, Booking


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    pass


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    pass
