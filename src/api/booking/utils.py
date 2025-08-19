from django.utils import timezone

def ensure_aware(dt):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt)
    return dt

def overlaps(start_a, end_a, start_b, end_b):
    start_a, end_a = ensure_aware(start_a), ensure_aware(end_a)
    start_b, end_b = ensure_aware(start_b), ensure_aware(end_b)
    return start_a < end_b and start_b < end_a

def is_slot_free(slot_start, slot_end, breaks, bookings):
    slot_start, slot_end = ensure_aware(slot_start), ensure_aware(slot_end)
    for b in breaks:
        if overlaps(slot_start, slot_end, b.start_time, b.end_time):
            return False
    for bk in bookings:
        if overlaps(slot_start, slot_end, bk.start_time, bk.end_time):
            return False
    return True
