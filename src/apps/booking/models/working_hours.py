from datetime import timedelta
from src.apps.common.models import BaseModel
from django.db import models
from django.utils import timezone
from src.apps.user.models import User

class WorkingHours(BaseModel):
    date = models.DateField()
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    barber = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.barber}: {self.from_hour.strftime('%H:%M')} - {self.to_hour.strftime('%H:%M')}"

    class Meta:
        verbose_name = "Ish vaqti"
        verbose_name_plural = "Ish vaqtlari"