from django.db import models
from src.apps.common.models import BaseModel


class Service(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    contact = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'service'
