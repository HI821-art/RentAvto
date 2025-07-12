# cart/models.py
from django.db import models
from car.models import Car  

class CartItem(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)  # Кількість днів оренди
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car} (x{self.quantity})"

    class Meta:
        ordering = ["added_at"]

    @property
    def total_price(self):
        return self.car.price_per_day * self.quantity