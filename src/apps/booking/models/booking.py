from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from src.apps.common.models import BaseModel
from .service import Service
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

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings',
        verbose_name="Xizmat"
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

    def __str__(self):
        return f"{self.user} uchun {self.service.name if self.service else 'Noma\'lum xizmat'} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        if not (self.start_time and self.service):
            return

        calculated_end_time = self.start_time + timedelta(minutes=self.service.duration)

        if self.start_time < timezone.now() and self._state.adding:
            raise ValidationError("O'tmishdagi vaqtga bron qilib bo'lmaydi.")

        overlapping_bookings = Booking.objects.filter(
            status=self.BookingStatus.CONFIRMED,
            start_time__lt=calculated_end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError("Bu vaqt oralig'i band. Iltimos, boshqa vaqt tanlang.")

        weekday = self.start_time.weekday()

        try:
            working_hours = WorkingHours.objects.get(weekday=weekday)
        except WorkingHours.DoesNotExist:
            raise ValidationError(f"{self.start_time.strftime('%A')} kuni dam olish kuni.")

        booking_start_time = self.start_time.time()
        booking_end_time = calculated_end_time.time()

        if not (working_hours.from_hour <= booking_start_time and working_hours.to_hour >= booking_end_time):
            raise ValidationError(
                f"Bron vaqti ish vaqtidan tashqarida. Ish vaqti: {working_hours.from_hour.strftime('%H:%M')} - {working_hours.to_hour.strftime('%H:%M')}")

    def save(self, *args, **kwargs):
        if self.start_time and self.service:
            self.end_time = self.start_time + timedelta(minutes=self.service.duration)

        self.clean()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ['start_time']
