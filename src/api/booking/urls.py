from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, WorkingHoursViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'working-hours', WorkingHoursViewSet, basename='workinghours')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]