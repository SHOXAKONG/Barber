from datetime import date, timedelta
from django.utils.dateparse import parse_date
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from src.apps.user.models import User
from src.apps.booking.models import WorkingHours, Booking
from src.apps.user.models import User
from src.apps.service.models import Service
from src.apps.breakes.models import Break
from .serializers import WorkingHoursSerializer, BookingCreateSerializer, BookingQuerySerializer, BookingSerializer
from django.shortcuts import get_object_or_404
from .utils import is_slot_free
from datetime import date, datetime


class WorkingHoursViewSet(viewsets.GenericViewSet):
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer

    @action(detail=False, methods=['get'], url_path='(?P<telegram_id>[^/.]+)')
    def get_barber_working_hours(self, request, telegram_id=None):
        barber = User.objects.get(telegram_id=telegram_id)

        working_hours = WorkingHours.objects.filter(barber=barber)

        serializer = WorkingHoursSerializer(working_hours, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.GenericViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return self.get_response(booking)

    def get_response(self, booking):
        return Response(
            {
                "id": booking.id,
                "message": "Booking successfully created",
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "barber": booking.barber_id,
                "service": booking.service_id,
            },
            status=201
        )

    def partial_update(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

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

        Booking.objects.filter(id=booking.id).update(
            status=Booking.BookingStatus.CANCELLED,
            cancel_reason=cancel_reason
        )

        return Response(
            {'success': f"Booking #{booking.id} muvaffaqiyatli bekor qilindi."},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        url_path=r'available-slots/(?P<date>\d{4}-\d{2}-\d{2})/(?P<barber_id>\d+)/(?P<service_id>\d+)'
    )
    def available_slots(self, request, date=None, barber_id=None, service_id=None):
        data = {
            "date": date,
            "barber_id": barber_id,
            "service_id": service_id,
        }
        serializer = BookingQuerySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        date = validated["date"]
        barber_id = validated["barber_id"]
        service_id = validated["service_id"]

        if not date or not service_id or not barber_id:
            return Response({"error": "barber_id, date and service_id are required"}, status=400)

        barber = get_object_or_404(User, pk=barber_id)
        service = get_object_or_404(Service, pk=service_id)

        duration = timedelta(minutes=service.duration_minutes)

        working_hours = get_object_or_404(
            WorkingHours, barber_id=barber_id, weekday=date.weekday()
        )

        start = datetime.combine(date, working_hours.from_hour)
        end = datetime.combine(date, working_hours.to_hour)

        breaks = Break.objects.filter(
            barber_id=barber_id,
            start_time__date=date
        )

        bookings = Booking.objects.filter(
            barber_id=barber_id,
            start_time__date=date
        )

        available_slots = []
        current = start

        while current + duration <= end:
            slot_end = current + duration

            if is_slot_free(current, slot_end, breaks, bookings):
                available_slots.append(current.strftime("%H:%M"))
            current += duration

        return Response({"available_slots": available_slots})

    @action(detail=False, methods=['get'], url_path='booking-history/(?P<telegram_id>[^/.]+)')
    def booking_history(self, request, telegram_id=None):
        telegram_id = telegram_id

        if not telegram_id:
            return Response(
                {"error": "telegram_id parametri kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        bookings = Booking.objects.filter(user=user).order_by('-start_time')
        serializer = BookingCreateSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            url_path=r'get_bookings/(?P<barber_id>[^/.]+)/(?P<date>\d{4}-\d{2}-\d{2})')
    def get_bookings(self, request, barber_id=None, date=None):
        user = get_object_or_404(User, id=barber_id)
        bookings = Booking.objects.filter(barber=user, start_time__date =date)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='get_bookings_by_id/(?P<booking_id>[^/.]+)')
    def get_bookings_by_id(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

# from .serializers import (
#     ServiceSerializer,
#     WorkingHoursSerializer,
#     BookingSerializer,
#     BookingCreateSerializer
# )


# class ServiceViewSet(viewsets.ModelViewSet):
#     queryset = Service.objects.all()
#     serializer_class = ServiceSerializer
#     permission_classes = [permissions.AllowAny]


# class WorkingHoursViewSet(viewsets.ModelViewSet):
#     serializer_class = WorkingHoursSerializer
#     permission_classes = [permissions.AllowAny]

#     def get_queryset(self):
#         return WorkingHours.objects.all()

#     def perform_create(self, serializer):
#         serializer.save()


# class BookingViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.AllowAny]

#     def get_serializer_class(self):
#         if self.action == 'create':
#             serializer = BookingCreateSerializer
#             print(serializer.data)
#             return serializer
#         return BookingSerializer

#     def get_queryset(self):
#         return Booking.objects.all().order_by('-start_time')

#     def perform_create(self, serializer):
#         telegram_id = serializer.validated_data.pop('telegram_id')
#         user, _ = User.objects.get_or_create(telegram_id=telegram_id)
#         serializer.save(user=user)
#         # print(serializer)

#     @action(detail=True, methods=['post'], url_path='cancel')
#     def cancel_booking(self, request, pk=None):
#         try:
#             booking = self.get_object()
#         except Booking.DoesNotExist:
#             return Response({'error': 'Booking topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

#         telegram_id = request.data.get('telegram_id')
#         cancel_reason = request.data.get('cancel_reason')

#         if not telegram_id:
#             return Response(
#                 {'error': 'telegram_id yuborilishi shart.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         if not cancel_reason:
#             return Response(
#                 {'error': 'cancel_reason yuborilishi shart.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if str(booking.user.telegram_id) != str(telegram_id):
#             return Response(
#                 {'error': 'Siz faqat o‘zingizning booking’ni bekor qilishingiz mumkin.'},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         if booking.status == Booking.BookingStatus.CANCELLED:
#             return Response({'error': 'Booking allaqachon bekor qilingan.'}, status=status.HTTP_400_BAD_REQUEST)

#         Booking.objects.filter(id=booking.id).update(
#             status=Booking.BookingStatus.CANCELLED,
#             cancel_reason=cancel_reason
#         )

#         return Response(
#             {'success': f"Booking #{booking.id} muvaffaqiyatli bekor qilindi."},
#             status=status.HTTP_200_OK
#         )

#     @action(detail=False, methods=['get'], url_path='available-slots')
#     def available_slots(self, request):
#         date_str = request.query_params.get('date')
#         service_id_str = request.query_params.get('service_id')

#         if not all([date_str, service_id_str]):
#             return Response(
#                 {"error": "'date' va 'service_id' parametrlarini to'liq kiriting."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
#             service = Service.objects.get(pk=int(service_id_str))
#             service_duration = service.duration
#         except (ValueError, Service.DoesNotExist):
#             return Response(
#                 {'error': "Sana formati yoki service_id noto'g'ri."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         weekday = target_date.weekday()
#         try:
#             working_hours = WorkingHours.objects.get(weekday=weekday)
#         except WorkingHours.DoesNotExist:
#             return Response({'weekday': target_date.strftime('%A'), 'slots': []})

#         tz = timezone.get_current_timezone()
#         now = timezone.localtime(timezone.now())

#         day_start = datetime.datetime.combine(target_date, working_hours.from_hour, tzinfo=tz)
#         day_end = datetime.datetime.combine(target_date, working_hours.to_hour, tzinfo=tz)

#         if target_date == now.date():
#             if now.minute < 30:
#                 start_minute = 30
#             else:
#                 now += datetime.timedelta(hours=1)
#                 start_minute = 0
#             start_time = now.replace(minute=start_minute, second=0, microsecond=0)
#             start_time = max(day_start, start_time)
#         else:
#             start_time = day_start

#         bookings_for_day = Booking.objects.filter(
#             start_time__date=target_date,
#             status=Booking.BookingStatus.CONFIRMED
#         )
#         booked_slots = [(b.start_time, b.end_time) for b in bookings_for_day]

#         available_slots_list = []
#         potential_time = start_time

#         while potential_time + datetime.timedelta(minutes=service_duration) <= day_end:
#             is_free = True
#             potential_end_time = potential_time + datetime.timedelta(minutes=service_duration)

#             for booked_start, booked_end in booked_slots:
#                 if potential_time < booked_end and potential_end_time > booked_start:
#                     is_free = False
#                     break

#             if is_free:
#                 available_slots_list.append(potential_time.strftime("%H:%M"))

#             potential_time += datetime.timedelta(minutes=30)

#         result = {'weekday': working_hours.get_weekday_display(), 'slots': available_slots_list}
#         return Response(result)

#     @action(detail=False, methods=['post'], url_path='cancel-day')
#     def cancel_day(self, request):
#         telegram_id = request.data.get('telegram_id') or request.query_params.get('telegram_id')

#         if not telegram_id:
#             return Response(
#                 {"error": "telegram_id parametri kerak."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user = User.objects.get(telegram_id=telegram_id)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "Foydalanuvchi topilmadi."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         if not user.is_staff:
#             return Response(
#                 {"error": "Faqat barber yoki admin bu amaliyotni bajarishi mumkin."},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         date_str = request.data.get('date')
#         reason = request.data.get('reason', 'Barber ushbu kundagi barcha bronlarni bekor qildi.')

#         if not date_str:
#             return Response(
#                 {"error": "'date' parametri kerak (format: YYYY-MM-DD)."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         target_date = parse_date(date_str)
#         if target_date is None:
#             return Response(
#                 {"error": "Sana formati noto‘g‘ri (YYYY-MM-DD)."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         bookings = Booking.objects.filter(
#             start_time__date=target_date,
#             status=Booking.BookingStatus.CONFIRMED
#         )

#         count = bookings.update(status=Booking.BookingStatus.CANCELLED, cancel_reason=reason)

#         return Response({
#             "success": f"{count} ta booking {target_date} uchun bekor qilindi.",
#             "reason": reason
#         }, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['post'], url_path='cancel-time-range')
#     def cancel_time_range(self, request):
#         telegram_id = request.query_params.get('telegram_id')

#         if not telegram_id:
#             return Response(
#                 {"error": "telegram_id parametri kerak."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user = User.objects.get(telegram_id=telegram_id)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "Foydalanuvchi topilmadi."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         if not user.is_staff:
#             return Response(
#                 {"error": "Faqat barber yoki admin bu amaliyotni bajarishi mumkin."},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         date_str = request.data.get('date')
#         from_time_str = request.data.get('from_time')
#         to_time_str = request.data.get('to_time')
#         reason = request.data.get(
#             'reason',
#             'Barber ushbu vaqt oralig‘idagi bronlarni bekor qildi.'
#         )

#         if not all([date_str, from_time_str, to_time_str]):
#             return Response(
#                 {"error": "'date', 'from_time', 'to_time' parametrlari kerak."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             target_date = parse_date(date_str)
#             if not target_date:
#                 raise ValueError("Invalid date format")
#             from_time = datetime.datetime.strptime(from_time_str, "%H:%M").time()
#             to_time = datetime.datetime.strptime(to_time_str, "%H:%M").time()
#         except ValueError:
#             return Response(
#                 {"error": "Sana yoki vaqt formati noto‘g‘ri."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         start_datetime = timezone.make_aware(
#             datetime.datetime.combine(target_date, from_time)
#         )
#         end_datetime = timezone.make_aware(
#             datetime.datetime.combine(target_date, to_time)
#         )

#         bookings = Booking.objects.filter(
#             start_time__gte=start_datetime,
#             end_time__lte=end_datetime,
#             status=Booking.BookingStatus.CONFIRMED
#         )

#         count = bookings.update(
#             status=Booking.BookingStatus.CANCELLED,
#             cancel_reason=reason
#         )

#         return Response(
#             {
#                 "success": f"{count} ta booking {date_str} {from_time_str}-{to_time_str} oralig‘ida bekor qilindi.",
#                 "reason": reason
#             },
#             status=status.HTTP_200_OK
#         )

#     @action(detail=False, methods=['get'], url_path='booking-history')
#     def booking_history(self, request):
#         telegram_id = request.query_params.get('telegram_id')

#         if not telegram_id:
#             return Response(
#                 {"error": "telegram_id parametri kerak."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user = User.objects.get(telegram_id=telegram_id)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "Foydalanuvchi topilmadi."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         bookings = Booking.objects.filter(user=user).order_by('-start_time')
#         serializer = BookingSerializer(bookings, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
