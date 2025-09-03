from django.contrib import admin
from .models import User
from .models import Roles


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'telegram_id',
                    'first_name',
                    'phone_number',
                    'language',
                    'default_from_hour',
                    'show_roles',
                    'default_to_hour')
    list_filter = ('roles',)

    def show_roles(self, obj):
        return ", ".join([r.name for r in obj.roles.all()])

    show_roles.short_description = "Roles"


@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
