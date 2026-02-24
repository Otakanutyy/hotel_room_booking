from django.db import models

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f"{self.name} - ${self.price_per_night} per night - Capacity: {self.capacity} beds"