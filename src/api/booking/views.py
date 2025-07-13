import datetime
from time import timezone
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from src.apps.user.models import User

from src.apps.booking.models import Service, WorkingHours, Booking
from .serializers import (
    ServiceSerializer,
    WorkingHoursSerializer,
    BookingSerializer,
    BookingCreateSerializer
)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class WorkingHoursViewSet(viewsets.ModelViewSet):
    serializer_class = WorkingHoursSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return WorkingHours.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        return Booking.objects.all().order_by('-start_time')

    def perform_create(self, serializer):
        telegram_id = serializer.validated_data.pop('telegram_id')
        user, _ = User.objects.get_or_create(telegram_id=telegram_id)
        serializer.save(user=user)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        try:
            booking = self.get_object()
        except Booking.DoesNotExist:
            return Response({'error': 'Booking topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        telegram_id = request.data.get('telegram_id')
        cancel_reason = request.data.get('cancel_reason')

        if not telegram_id:
            return Response(
                {'error': 'telegram_id yuborilishi shart.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not cancel_reason:
            return Response(
                {'error': 'cancel_reason yuborilishi shart.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(booking.user.telegram_id) != str(telegram_id):
            return Response(
                {'error': 'Siz faqat o‘zingizning booking’ni bekor qilishingiz mumkin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if booking.status == Booking.BookingStatus.CANCELLED:
            return Response({'error': 'Booking allaqachon bekor qilingan.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.BookingStatus.CANCELLED
        booking.cancel_reason = cancel_reason
        booking.save()

        return Response(
            {'success': f"Booking #{booking.id} muvaffaqiyatli bekor qilindi."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='available-slots')
    def available_slots(self, request):
        date_str = request.query_params.get('date')
        service_id_str = request.query_params.get('service_id')

        if not all([date_str, service_id_str]):
            return Response(
                {"error": "'date' va 'service_id' parametrlarini to'liq kiriting."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            service = Service.objects.get(pk=int(service_id_str))
            service_duration = service.duration
        except (ValueError, Service.DoesNotExist):
            return Response(
                {'error': "Sana formati yoki service_id noto'g'ri."},
                status=status.HTTP_400_BAD_REQUEST
            )

        weekday = target_date.weekday()
        try:
            working_hours = WorkingHours.objects.get(weekday=weekday)
        except WorkingHours.DoesNotExist:
            return Response({'weekday': target_date.strftime('%A'), 'slots': []})

        tz = timezone.get_current_timezone()
        now = timezone.localtime(timezone.now())

        day_start = datetime.datetime.combine(target_date, working_hours.from_hour, tzinfo=tz)
        day_end = datetime.datetime.combine(target_date, working_hours.to_hour, tzinfo=tz)

        if target_date == now.date():
            if now.minute < 30:
                start_minute = 30
            else:
                now += datetime.timedelta(hours=1)
                start_minute = 0
            start_time = now.replace(minute=start_minute, second=0, microsecond=0)
            start_time = max(day_start, start_time)
        else:
            start_time = day_start

        bookings_for_day = Booking.objects.filter(
            start_time__date=target_date,
            status=Booking.BookingStatus.CONFIRMED
        )
        booked_slots = [(b.start_time, b.end_time) for b in bookings_for_day]

        available_slots_list = []
        potential_time = start_time

        while potential_time + datetime.timedelta(minutes=service_duration) <= day_end:
            is_free = True
            potential_end_time = potential_time + datetime.timedelta(minutes=service_duration)

            for booked_start, booked_end in booked_slots:
                if potential_time < booked_end and potential_end_time > booked_start:
                    is_free = False
                    break

            if is_free:
                available_slots_list.append(potential_time.strftime("%H:%M"))

            potential_time += datetime.timedelta(minutes=30)

        result = {'weekday': working_hours.get_weekday_display(), 'slots': available_slots_list}
        return Response(result)

    @action(detail=False, methods=['post'], url_path='cancel-day')
    def cancel_day(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {"error": "Faqat barber yoki admin bu amaliyotni bajarishi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )

        date_str = request.data.get('date')
        reason = request.data.get('reason', 'Barber ushbu kundagi barcha bronlarni bekor qildi.')

        if not date_str:
            return Response({"error": "'date' parametri kerak (format: YYYY-MM-DD)."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = parse_date(date_str)
            if not target_date:
                raise ValueError
        except ValueError:
            return Response({"error": "Sana formati noto‘g‘ri (YYYY-MM-DD)."},
                            status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(
            start_time__date=target_date,
            status=Booking.BookingStatus.CONFIRMED
        )

        count = bookings.update(status=Booking.BookingStatus.CANCELLED, cancel_reason=reason)

        return Response({
            "success": f"{count} ta booking {target_date} uchun bekor qilindi.",
            "reason": reason
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='cancel-time-range')
    def cancel_time_range(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {"error": "Faqat barber yoki admin bu amaliyotni bajarishi mumkin."},
                status=status.HTTP_403_FORBIDDEN
            )

        date_str = request.data.get('date')
        from_time_str = request.data.get('from_time')  # format: "HH:MM"
        to_time_str = request.data.get('to_time')      # format: "HH:MM"
        reason = request.data.get('reason', 'Barber ushbu vaqt oralig‘idagi bronlarni bekor qildi.')

        if not all([date_str, from_time_str, to_time_str]):
            return Response({"error": "'date', 'from_time', 'to_time' parametrlari kerak."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = parse_date(date_str)
            from_time = timezone.datetime.strptime(from_time_str, "%H:%M").time()
            to_time = timezone.datetime.strptime(to_time_str, "%H:%M").time()
        except ValueError:
            return Response({"error": "Sana yoki vaqt formati noto‘g‘ri."},
                            status=status.HTTP_400_BAD_REQUEST)

        start_datetime = timezone.make_aware(timezone.datetime.combine(target_date, from_time))
        end_datetime = timezone.make_aware(timezone.datetime.combine(target_date, to_time))

        bookings = Booking.objects.filter(
            start_time__gte=start_datetime,
            end_time__lte=end_datetime,
            status=Booking.BookingStatus.CONFIRMED
        )

        count = bookings.update(status=Booking.BookingStatus.CANCELLED, cancel_reason=reason)

        return Response({
            "success": f"{count} ta booking {date_str} {from_time_str}-{to_time_str} oralig‘ida bekor qilindi.",
            "reason": reason
        }, status=status.HTTP_200_OK)
