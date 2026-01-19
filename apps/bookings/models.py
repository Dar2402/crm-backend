from django.db import models
from django.conf import settings
from apps.candidates.models import Candidate


User = settings.AUTH_USER_MODEL


class ApplicationStage(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="bookings")

    current_stage = models.ForeignKey(
        ApplicationStage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="current_bookings",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -> {self.candidate}"


class StageHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="stage_history")
    stage = models.ForeignKey(ApplicationStage, on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.booking} - {self.stage}"
