from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        (0, "Admin"),
        (1, "User"),
    ]
    role = models.IntegerField(choices=ROLE_CHOICES, default=1)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, blank=True, null=True)


    def __str__(self):
        return self.username