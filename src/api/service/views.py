from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from src.apps.service.models import ServiceType, Service
from src.api.service.serializers import ServiceTypeSerializer, ServiceSerializer
from rest_framework.decorators import action
from src.apps.user.models.users import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer

    @swagger_auto_schema(
        operation_summary="ServiceType ro'yxati",
        operation_description="Barcha ServiceType obyektlarini ro'yxatini olish.",
        responses={200: ServiceTypeSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Yangi ServiceType qo'shish",
        operation_description="Yangi ServiceType obyektini qo'shish. Masalan: 'Strijka', 'Brityo', 'Massaj'.",
        responses={201: ServiceTypeSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ServiceType olish (ID bo'yicha)",
        operation_description="ServiceType obyektini ID orqali olish.",
        responses={200: ServiceTypeSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ServiceType yangilash (PUT)",
        operation_description="ServiceType obyektini to'liq yangilash.",
        responses={200: ServiceTypeSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ServiceType qisman yangilash (PATCH)",
        operation_description="ServiceType obyektini faqat kerakli qismlarini yangilash.",
        responses={200: ServiceTypeSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ServiceType o'chirish",
        operation_description="ServiceType obyektini o'chirish (ID bo'yicha).",
        responses={204: 'Successfully deleted'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Barberning service larini olish uchun!",
        operation_description="Barberga tegishli bo'lgan service va obyektlarni berish uchun!",
        responses={204: 'Successfully deleted'}
    )
    @action(detail=False, methods=['get'], url_path='(?P<telegram_id>[^/.]+)')
    def get_barber_service_types(self, request, telegram_id=None):
        barber = get_object_or_404(User, telegram_id=telegram_id, roles__name='Barber')

        servicetypes = ServiceType.objects.filter(barber = barber)

        serializer = ServiceTypeSerializer(servicetypes, many=True)
        return Response(serializer.data)
    
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    @swagger_auto_schema(
        operation_summary="Service ro'yxati",
        operation_description="Barcha service jadvalidagi ma'lumotlarni olish uchun!",
        responses={200: ServiceSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Service qo'shish",
        operation_description="Service modeliga yangi obyekt qo'shish uchun!\nMasalan: Service Type - Strijka bo'lsa, bu strijkaning turi.",
        responses={201: ServiceSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Service olish (ID bo'yicha)",
        operation_description="Berilgan ID bo'yicha Service modelidagi bitta obyektni olish uchun.",
        responses={200: ServiceSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Service yangilash (PUT)",
        operation_description="ID bo'yicha mavjud service obyektini to'liq yangilash.",
        responses={200: ServiceSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Service qisman yangilash (PATCH)",
        operation_description="ID bo'yicha mavjud service obyektini faqat kerakli qismlarini yangilash.",
        responses={200: ServiceSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Service o'chirish",
        operation_description="ID bo'yicha service obyektini o'chirish.",
        responses={204: 'Successfully deleted'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Barberning service larini olish uchun!",
        operation_description="Barberga tegishli bo'lgan service va obyektlarni berish uchun!",
        responses={204: 'Successfully deleted'}
    )
    @action(detail=True, methods=['get'])
    def get_services(self, request, pk=None):
        servicetype = get_object_or_404(ServiceType, pk=pk)

        service = Service.objects.filter(service_type = servicetype)

        serializer = ServiceSerializer(service, many=True)
        return Response(serializer.data)