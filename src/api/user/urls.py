from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('register', views.RegisterViewSet, 'register')
router.register('users', views.UsersViewSet, 'users')
router.register('update_lang', views.UpdateViewSet, 'update_lang')

urlpatterns = [
    path('', include(router.urls)),
]
