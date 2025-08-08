from django.urls import path, include

urlpatterns = [
    path('auth/', include('src.api.user.urls')),
    path('booking/', include('src.api.booking.urls')),
    path('service/', include('src.api.service.urls')),
    path('break/', include('src.api.breakes.urls')),
]