from django.contrib import admin
from src.apps.service.models import Service, ServiceType
# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_type', 'name', 'description', 'duration', 'price')

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'barber', 'name')