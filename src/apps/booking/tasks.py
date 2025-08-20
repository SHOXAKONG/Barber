from celery import shared_task
from django.utils import timezone
from .models import Booking

@shared_task
def update_completed_bookings():
    now = timezone.now()
    Booking.objects.filter(end_time__lt=now, status="CONFIRMED").update(status="COMPLETED")
