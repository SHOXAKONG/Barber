import datetime
from django.utils import timezone
from .models import Booking, WorkingHours, Service


def get_available_slots(target_date: datetime.date, service_id: int) -> dict:
    try:
        service = Service.objects.get(pk=service_id)
        service_duration = service.duration
    except Service.DoesNotExist:
        return {'error': "Xizmat topilmadi."}

    weekday = target_date.weekday()
    try:
        working_hours = WorkingHours.objects.get(weekday=weekday)
    except WorkingHours.DoesNotExist:
        return {'weekday': target_date.strftime('%A'), 'slots': []}

    now = timezone.now()
    tz = timezone.get_current_timezone()
    day_start = tz.localize(datetime.datetime.combine(target_date, working_hours.from_hour))
    day_end = tz.localize(datetime.datetime.combine(target_date, working_hours.to_hour))

    start_time = day_start

    if target_date == now.date():
        if now.minute < 30:
            rounded_time = now.replace(minute=30, second=0, microsecond=0)
        else:
            rounded_time = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        if rounded_time > start_time:
            start_time = rounded_time

    bookings_for_day = Booking.objects.filter(
        status=Booking.BookingStatus.CONFIRMED,
        start_time__date=target_date
    )
    booked_slots = [(b.start_time, b.end_time) for b in bookings_for_day]

    available_slots = []
    potential_time = start_time

    while potential_time + datetime.timedelta(minutes=service_duration) <= day_end:
        is_free = True
        potential_end_time = potential_time + datetime.timedelta(minutes=service_duration)

        for booked_start, booked_end in booked_slots:
            if potential_time < booked_end and potential_end_time > booked_start:
                is_free = False
                break

        if is_free:
            available_slots.append(potential_time.strftime("%H:%M"))

        potential_time += datetime.timedelta(minutes=30)

    return {'weekday': working_hours.get_weekday_display(), 'slots': available_slots}
