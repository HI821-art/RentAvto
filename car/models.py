# car/models.py
from django.db import models


class Car(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    year = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    consumption = models.FloatField()
    color = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='cars/')

    def __str__(self):
        return f"{self.brand} {self.model}"

    class Meta:
        ordering = ["brand", "model"]

class Booking(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=100)
    date_from = models.DateField()
    date_to = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Очікує підтвердження'),
            ('confirmed', 'Підтверджено'),
            ('canceled', 'Скасовано')
        ],
        default='pending'
    )

    def __str__(self):
        return f"Booking for {self.car} by {self.name} ({self.status})"

    class Meta:
        ordering = ["created_at"]

    @property
    def total_price(self):
        return self.car.price_per_day * (self.date_to - self.date_from).days