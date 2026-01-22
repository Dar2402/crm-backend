from django.db import models
from django.conf import settings
from apps.candidates.models import Candidate

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    STATUS = (
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=10, default="INR")

    provider = models.CharField(max_length=20, default="razorpay")

    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS, default="created")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["razorpay_order_id"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.amount} - {self.status}"


