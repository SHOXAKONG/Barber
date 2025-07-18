from django.urls import path, include

urlpatterns = [
    path('auth/', include('src.api.user.urls')),
    path('', include('src.api.booking.urls'))
]
