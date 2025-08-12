from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from src.apps.common.models import BaseModel
from src.apps.service.models import Service
from .working_hours import WorkingHours

class Booking(BaseModel):
    class BookingStatus(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Tasdiqlangan'
        COMPLETED = 'COMPLETED', 'Bajarilgan'
        CANCELLED = 'CANCELLED', 'Bekor qilingan'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Mijoz"
    )

    start_time = models.DateTimeField(verbose_name="Boshlanish vaqti")
    end_time = models.DateTimeField(verbose_name="Tugash vaqti", blank=True)

    status = models.CharField(
        max_length=10,
        choices=BookingStatus.choices,
        default=BookingStatus.CONFIRMED,
        verbose_name="Holati"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="Mijoz izohi")
    cancel_reason = models.TextField(null=True, blank=True)

    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ['start_time']