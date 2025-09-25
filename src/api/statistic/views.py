import calendar
from datetime import timedelta

from django.db.models import Count, Avg
from django.db.models.functions import ExtractIsoWeekDay
from django.utils.timezone import now
from rest_framework.decorators import action

from .serializers import WeeklyClientsSerializer, BarberActivitySerializer, ServiceUsageSerializer, \
    BarberRatingSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from src.apps.booking.models import Booking
from ...apps.user.models import User


class WeeklyClientViewSet(viewsets.GenericViewSet):
    serializer_class = WeeklyClientsSerializer
    queryset = Booking.objects.all()

    def list(self, request):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        queryset = (
            Booking.objects.filter(start_time__gte=start_of_week, start_time__lt=end_of_week)
            .annotate(weekday=ExtractIsoWeekDay("start_time"))
            .values("weekday")
            .annotate(client=Count("user", distinct=True))
            .order_by("weekday")
        )

        weekdays_map = {
            1: "Dushanba",
            2: "Seshanba",
            3: "Chorshanba",
            4: "Payshanba",
            5: "Juma",
            6: "Shanba",
            7: "Yakshanba",
        }

        result_dict = {item["weekday"]: item["client"] for item in queryset}

        data = [
            {"weekday": i, "clients": result_dict.get(i, 0)}
            for i in range(1, 8)
        ]

        serializer = self.get_serializer(data, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def barber_activity(self, request):
        today = now().date()

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        start_of_month = today.replace(day=1)
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=days_in_month) + timedelta(days=1)

        monthly = (
            Booking.objects.filter(start_time__gte=start_of_month, start_time__lt=end_of_month)
            .values("barber__id", "barber__first_name")
            .annotate(monthly_clients=Count("user", distinct=True))
        )

        weekly = (
            Booking.objects.filter(start_time__gte=start_of_week, start_time__lt=end_of_week)
            .values("barber__id")
            .annotate(weekly_clients=Count("user", distinct=True))
        )

        weekly_map = {item["barber__id"]: item["weekly_clients"] for item in weekly}

        data = [
            {
                "barber_id": item["barber__id"],
                "barber_name": item["barber__first_name"],
                "monthly_clients": item["monthly_clients"],
                "weekly_clients": weekly_map.get(item["barber__id"], 0),
            }
            for item in monthly
        ]

        serializer = BarberActivitySerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def top_services(self, request):
        today = now().date()

        start_of_month = today.replace(day=1)
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=days_in_month) + timedelta(days=1)

        queryset = (
            Booking.objects.filter(start_time__gte=start_of_month, start_time__lt=end_of_month)
            .values("service__id", "service__name")
            .annotate(usage_count=Count("id"))
            .order_by("-usage_count")
        )

        serializer = ServiceUsageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def barber_rating(self, request):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)

        active_barbers = Booking.objects.filter(
            start_time__gte=start_of_week, start_time__lt=end_of_week
        ).values_list("barber_id", flat=True).distinct()

        queryset = (
            User.objects.filter(id__in=active_barbers, roles__name="Barber")
            .values("id", "first_name", "rating")
            .order_by("-rating")
        )

        serializer = BarberRatingSerializer(queryset, many=True)
        return Response(serializer.data)
