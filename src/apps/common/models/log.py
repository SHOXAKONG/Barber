from django.db import models
from django.utils import timezone
from django.conf import settings

class Log(models.Model):
    LEVEL_CHOICES = (
        ("INFO", "INFO"),
        ("WARNING", "WARNING"),
        ("ERROR", "ERROR"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=255)  
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="INFO")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.level}] {self.user} - {self.action}"
