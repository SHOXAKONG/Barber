from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from src.apps.service.models import ServiceType, Service
from src.api.service.serializers import ServiceTypeSerializer, ServiceSerializer, ServiceTypeOnlySerializer
from rest_framework.decorators import action
from src.apps.user.models.users import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import DestroyModelMixin, ListModelMixin

class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    
    @action(detail=False, methods=['get'], url_path='by-telegram/(?P<telegram_id>[^/.]+)')
    def get_barber_service_types(self, request, telegram_id=None):
        barber = get_object_or_404(User, telegram_id=telegram_id, roles__name='Barber')
        servicetypes = ServiceType.objects.filter(barber=barber)
        serializer = ServiceTypeSerializer(servicetypes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='only-type-by-telegram/(?P<telegram_id>[^/.]+)')
    def get_all_services(self, request, telegram_id=None):
        barber = get_object_or_404(User, telegram_id=telegram_id, roles__name='Barber')
        servicetypes = ServiceType.objects.filter(barber=barber)
        serializer = ServiceTypeOnlySerializer(servicetypes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    @action(detail=True, methods=['get'])
    def get_services(self, request, pk=None):
        servicetype = get_object_or_404(ServiceType, pk=pk)

        service = Service.objects.filter(service_type = servicetype)

        serializer = ServiceSerializer(service, many=True)
        return Response(serializer.data)