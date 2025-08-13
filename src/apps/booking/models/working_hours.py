from src.apps.common.models import BaseModel
from django.db import models
from src.apps.user.models import User
from django.db.models import F, Func, DateTimeField
from django.utils import timezone

class WorkingHoursQuerySet(models.QuerySet):
    def future(self):
        now = timezone.now()
        return self.annotate(
            to_datetime=Func(
                F('date'),
                F('to_hour'),
                function='MAKE_TIMESTAMP',  # PostgreSQL
                output_field=DateTimeField()
            )
        ).filter(to_datetime__gt=now)


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

    weekday = models.IntegerField(choices=WEEKDAYS)

    from_hour = models.TimeField()
    to_hour = models.TimeField()

    barber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='working_hours')

    def __str__(self):
        return f"{self.barber}: {self.weekday}"
    
    def is_past(self):
        return self.to_hour>timezone.now()

    objects = WorkingHoursQuerySet.as_manager()

    class Meta:
        verbose_name = "Ish vaqti"
        verbose_name_plural = "Ish vaqtlari"