from apps.candidates.models import Candidate
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

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

    def clean(self):
        """
        Enforce booking invariants at model level
        """
        super().clean()

        # Rule 1: completed booking must imply deployed candidate
        if self.status == "completed":
            if self.candidate.status != "deployed":
                raise ValidationError(
                    "Completed booking requires candidate to be deployed"
                )

        # Rule 2: rejected booking cannot keep candidate booked
        if self.status == "rejected":
            if self.candidate.status != "available":
                raise ValidationError(
                    "Rejected booking requires candidate to be available"
                )

        # Rule 3: only one active booking per candidate
        if self.status == "active":
            qs = Booking.objects.filter(
                candidate=self.candidate,
                status="active",
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError(
                    "Candidate already has an active booking"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StageHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="stage_history")
    stage = models.ForeignKey(ApplicationStage, on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.booking} - {self.stage}"

    def clean(self):
        super().clean()

        # Prevent backward stage history
        last = (
            StageHistory.objects
            .filter(booking=self.booking)
            .order_by("-updated_at")
            .first()
        )

        if last and self.stage.order < last.stage.order:
            raise ValidationError(
                "Cannot add backward stage history entry"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
