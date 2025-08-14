from datetime import timedelta, datetime, time
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from src.apps.common.models import BaseModel
from src.apps.service.models import Service
from src.apps.breakes.models import Break
from .working_hours import WorkingHours
import pytz

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

    barber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='barber_booking',
        verbose_name="Usta"
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

    def clean(self):
        super().clean()

        tashkent_tz = pytz.timezone('Asia/Tashkent')
        now = timezone.now().astimezone(tashkent_tz)

        weekday = self.start_time.weekday()
        try:
            working_hours = WorkingHours.objects.get(barber=self.barber, weekday=weekday)
        except WorkingHours.DoesNotExist:
            raise ValidationError("Barber bu soatlarda ishlamaydi.")

        working_start = timezone.make_aware(
            datetime.combine(self.start_time.date(), working_hours.from_hour),
            tzinfo=tashkent_tz
        )
        working_end = timezone.make_aware(
            datetime.combine(self.start_time.date(), working_hours.to_hour),
            tzinfo=tashkent_tz
        )

        if not (working_start <= self.start_time and self.end_time <= working_end):
            raise ValidationError("Booking must be within the barber's working hours.")

        if self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Boshlanish vaqti tugash vaqtidan oldin bo‘lishi kerak.")

        if not self.end_time and self.service_id:
            duration = timedelta(minutes=self.service.duration_minutes)
            self.end_time = self.start_time + duration

        min_allowed_date = now + timedelta(days=30)
        if self.start_time < min_allowed_date:
            raise ValidationError("30 kundan otib ketdi")

        if self.start_time < now:
            raise ValidationError("O'tmishdagi kunga bron qila olmaysiz.")

        day_start = timezone.make_aware(
            datetime.combine(self.start_time.date(), time.min),
            tzinfo=tashkent_tz
        )
        day_end = timezone.make_aware(
            datetime.combine(self.start_time.date(), time.max),
            tzinfo=tashkent_tz
        )

        breaks = Break.objects.filter(
            barber=self.barber,
            start_time__gte=day_start,
            start_time__lte=day_end
        )
        bookings = Booking.objects.filter(
            barber=self.barber,
            start_time__gte=day_start,
            start_time__lte=day_end
        ).exclude(pk=self.pk)

        def overlaps(s1, e1, s2, e2):
            return s1 < e2 and s2 < e1

        for b in breaks:
            if overlaps(self.start_time, self.end_time, b.start_time, b.end_time):
                raise ValidationError("Bu vaqt oralig‘i barber break qiladi.")

        for bk in bookings:
            if overlaps(self.start_time, self.end_time, bk.start_time, bk.end_time):
                raise ValidationError("Buyoda bron boru.")