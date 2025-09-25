from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register('weekly', views.WeeklyClientViewSet, 'weekly')

urlpatterns = [
    path('', include(router.urls))
]