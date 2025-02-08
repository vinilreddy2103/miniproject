from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

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

class Habit(models.Model):
    TYPE_CHOICES = [
        ("measurable", "Measurable"),
        ("non-measurable", "Non-Measurable"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Each habit belongs to a user
    name = models.CharField(max_length=255)
    habit_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    target_count = models.PositiveIntegerField(default=1)  # Target count for measurable habits
    current_count = models.PositiveIntegerField(default=0)  # Tracks progress
    
    completed = models.BooleanField(default=False)
    date = models.DateField(default=date.today)  # Helps reset habits daily

    def update_progress(self, increment=1):
        """Increments progress and marks habit as completed if target is reached."""
        if self.habit_type == "measurable":
            self.current_count += increment
            if self.current_count >= self.target_count:
                self.completed = True
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.name} ({self.habit_type})"
