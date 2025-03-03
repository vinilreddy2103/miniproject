from django.db import models
from datetime import date
from authentication.models import CustomUser

def get_today():
    return date.today()

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
    date = models.DateField(default=get_today)  # Changed lambda to function
    last_reset_date = models.DateField(default=get_today)  # Changed lambda to function

    # New Fields
    last_completed = models.DateField(null=True, blank=True)  # Stores last completed date
    streak = models.PositiveIntegerField(default=0)  # Tracks the streak count

    def update_progress(self, increment=1):
        """Increments progress and marks habit as completed if target is reached."""
        if self.habit_type == "measurable":
            self.current_count += increment
            if self.current_count >= self.target_count:
                self.completed = True
                self.update_streak()
        self.save()

    def update_streak(self):
        """Updates the habit streak based on the last completed date."""
        today = get_today()
        
        if self.last_completed:
            days_since_last = (today - self.last_completed).days
            if days_since_last > 1:
                self.streak = 1  # Reset streak if a day is missed, but count today
            elif days_since_last == 1:
                self.streak += 1  # Increase streak if completed consecutively
            # If completed on the same day, keep the streak unchanged
        else:
            self.streak = 1  # Start streak if it's the first completion

        # Update the last completed date
        self.last_completed = today
        self.save()


    def __str__(self):
        return f"{self.user.email} - {self.name} ({self.habit_type}) | Streak: {self.streak}"
