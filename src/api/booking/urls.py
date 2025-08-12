from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('working-hours', views.WorkingHoursViewSet, 'working-hours')
router.register('', views.BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]