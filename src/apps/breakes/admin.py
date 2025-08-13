from django.contrib import admin
from .models import Break
# Register your models here.
@admin.register(Break)
class BreakAdmin(admin.ModelAdmin):
    list_display = ('__str__','start_time', 'end_time', 'barber', 'reason')