from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):  
    username = models.CharField(max_length=150, unique=True)  # Explicit username field
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Managed by Django

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",  # Avoids conflict
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",  # Avoids conflict
        blank=True
    )

    def __str__(self):
        return self.username


