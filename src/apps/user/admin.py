from django.contrib import admin
from .models import User
from .models import Roles

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'first_name', 'phone_number', 'name', 'rating', 'default_from_hour', 'default_to_hour', 'photo', 'rating')

@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('id','name')