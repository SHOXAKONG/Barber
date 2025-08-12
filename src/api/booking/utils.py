def overlaps(start_a, end_a, start_b, end_b):
    return start_a < end_b and start_b < end_a

def is_slot_free(slot_start, slot_end, breaks, bookings):
    for b in breaks:
        if overlaps(slot_start, slot_end, b.start_time, b.end_time):
            return False
    for bk in bookings:
        if overlaps(slot_start, slot_end, bk.start_time, bk.end_time):
            return False
    return True