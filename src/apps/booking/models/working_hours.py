from datetime import timedelta
from src.apps.common.models import BaseModel
from django.db import models
from django.utils import timezone
from src.apps.user.models import User


class WorkingHours(BaseModel):
    WEEKDAYS = [
        (0, "Dushanba"),
        (1, "Seshanba"),
        (2, "Chorshanba"),
        (3, "Payshanba"),
        (4, "Juma"),
        (5, "Shanba"),
        (6, "Yakshanba"),
    ]

    weekday = models.IntegerField(choices=WEEKDAYS, unique=True)
    from_hour = models.TimeField(default=timezone.now)
    to_hour = models.TimeField(default=timezone.now() + timedelta(hours=8))
    barber = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_weekday_display()}: {self.from_hour.strftime('%H:%M')} - {self.to_hour.strftime('%H:%M')}"

    class Meta:
        verbose_name = "Ish vaqti"
        verbose_name_plural = "Ish vaqtlari"
        ordering = ['weekday']
