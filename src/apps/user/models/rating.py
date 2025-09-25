from django.db import models
from src.apps.common.models import BaseModel


class Rating(BaseModel):
    rating = models.FloatField()
    barber = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="ratings")
    client = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="given_ratings")

    class Meta:
        db_table = 'rating'

    def __str__(self):
        return self.rating
