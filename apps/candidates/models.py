from django.core.exceptions import ValidationError
from django.db import models


class Candidate(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("booked", "Booked"),
        ("deployed", "Deployed"),
    )

    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    religion = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=50, blank=True)

    nationality = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    languages = models.CharField(max_length=255, blank=True)  # comma separated

    applied_for = models.CharField(max_length=150)
    expected_workplace = models.CharField(max_length=150, blank=True)
    expected_salary = models.IntegerField(null=True, blank=True)

    education = models.CharField(max_length=150, blank=True)
    google_map = models.BooleanField(default=False)

    vehicle_known = models.CharField(max_length=255, blank=True)
    vehicle_transmission = models.CharField(max_length=50, blank=True)

    departure_from_india_days = models.PositiveIntegerField(null=True, blank=True)

    price_sar = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    def clean(self):
        """
        Enforce candidate-booking consistency
        """
        super().clean()

        active_bookings = self.bookings.filter(status="active").count()
        completed_bookings = self.bookings.filter(status="completed").count()

        if self.status == "available":
            if active_bookings > 0:
                raise ValidationError(
                    "Available candidate cannot have active bookings"
                )

        if self.status == "booked":
            if active_bookings != 1:
                raise ValidationError(
                    "Booked candidate must have exactly one active booking"
                )

        if self.status == "deployed":
            if completed_bookings != 1:
                raise ValidationError(
                    "Deployed candidate must have exactly one completed booking"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CandidatePhoto(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="candidates/photos/")

    def __str__(self):
        return f"{self.candidate.full_name} photo"


class CandidateExperience(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="experiences")

    job_title = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    period_years = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job_title}"


class CandidateSkill(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="skills")
    skill_name = models.CharField(max_length=100)

    def __str__(self):
        return self.skill_name


class CandidatePassport(models.Model):
    PASSPORT_TYPE = (
        ("ECNR", "ECNR"),
        ("ECR", "ECR"),
    )

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name="passport")

    passport_number = models.CharField(max_length=50)
    passport_type = models.CharField(max_length=10, choices=PASSPORT_TYPE)

    date_of_issue = models.DateField()
    date_of_expiry = models.DateField()
    place_of_issue = models.CharField(max_length=100)

    date_of_birth = models.DateField()

    passport_in_office = models.BooleanField(default=True)

    def __str__(self):
        return self.passport_number


class CandidateMedical(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name="medical")

    is_medically_fit = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.candidate.full_name} medical"
