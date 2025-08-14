from django.db import models
from src.apps.user.models import User
from django.utils import timezone
from datetime import timedelta

class ServiceType(models.Model):
    barber = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Service(models.Model):
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    duration = models.DurationField(default=timedelta(minutes=30))
    price = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.service_type.name})"
    
    @property
    def duration_minutes(self):
        return int(self.duration.total_seconds() // 60)
    

    class Meta:
        db_table = 'service'