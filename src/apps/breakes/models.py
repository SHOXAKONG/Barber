from django.db import models
from src.apps.user.models.users import User
from django.utils import timezone

class Break(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()

    @property
    def is_past(self):
        return timezone.now() > self.end_time

    def __str__(self):
        return f'{self.user.name}: {self.start_time} + {self.end_time}'