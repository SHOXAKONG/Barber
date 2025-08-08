# src/apps/breaking/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from src.api.breakes.views import BreakModelViewSet

router = DefaultRouter()
router.register(r'breaks', BreakModelViewSet, basename='break')

urlpatterns = [
    path('', include(router.urls)),
]
