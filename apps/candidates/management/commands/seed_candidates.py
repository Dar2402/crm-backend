import random
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

from faker import Faker

from apps.candidates.models import (
    Candidate,
    CandidatePhoto,
    CandidateExperience,
    CandidateSkill,
    CandidatePassport,
    CandidateMedical,
)

fake = Faker()


class Command(BaseCommand):
    help = "Seed dummy candidate data with related models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of candidates to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(self.style.WARNING(f"Seeding {count} candidates..."))

        created = 0

        for _ in range(count):
            candidate = self.create_candidate()
            self.create_photos(candidate)
            self.create_experiences(candidate)
            self.create_skills(candidate)
            self.create_passport(candidate)
            self.create_medical(candidate)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully created {created} candidates"))

    # -----------------------------
    # Creation helpers
    # -----------------------------

    def create_candidate(self):
        statuses = ["available", "booked", "deployed"]
        applied_roles = ["Driver", "House Maid", "Cook", "Cleaner", "Office Boy"]

        candidate = Candidate.objects.create(
            full_name=fake.name(),
            age=random.randint(21, 45),
            religion=random.choice(["Hindu", "Muslim", "Christian", "Sikh", ""]),
            marital_status=random.choice(["Single", "Married", ""]),
            nationality=random.choice(["Indian", "Nepali", "Sri Lankan"]),
            region=fake.state(),
            languages=", ".join(random.sample(["Hindi", "English", "Tamil", "Urdu"], k=2)),
            applied_for=random.choice(applied_roles),
            expected_workplace=random.choice(["Home", "Office", "Hotel", ""]),
            expected_salary=random.randint(1200, 3000),
            education=random.choice(["10th", "12th", "Graduate", ""]),
            google_map=random.choice([True, False]),
            vehicle_known=random.choice(["Car", "Bike", "None"]),
            vehicle_transmission=random.choice(["Manual", "Automatic", ""]),
            departure_from_india_days=random.randint(10, 60),
            price_sar=random.randint(8000, 15000),
            status=random.choice(statuses),
        )

        return candidate

    def create_photos(self, candidate):
        # Create 1–3 dummy image placeholders
        for i in range(random.randint(1, 3)):
            image_content = ContentFile(self.fake_image_bytes(), name=f"{fake.uuid4()}.jpg")
            CandidatePhoto.objects.create(candidate=candidate, image=image_content)

    def create_experiences(self, candidate):
        for _ in range(random.randint(1, 3)):
            CandidateExperience.objects.create(
                candidate=candidate,
                job_title=random.choice(["Driver", "Helper", "Cleaner", "Cook"]),
                country=random.choice(["India", "UAE", "Saudi", "Qatar"]),
                city=fake.city(),
                period_years=random.randint(1, 5),
            )

    def create_skills(self, candidate):
        skills = random.sample(
            ["Driving", "Cooking", "Cleaning", "Babysitting", "Office Work", "Delivery"],
            k=random.randint(2, 4),
        )
        for skill in skills:
            CandidateSkill.objects.create(candidate=candidate, skill_name=skill)

    def create_passport(self, candidate):
        issue_date = fake.date_between(start_date="-8y", end_date="-2y")
        expiry_date = issue_date + timedelta(days=10 * 365)

        CandidatePassport.objects.create(
            candidate=candidate,
            passport_number=fake.bothify(text="P########"),
            passport_type=random.choice(["ECNR", "ECR"]),
            date_of_issue=issue_date,
            date_of_expiry=expiry_date,
            place_of_issue=fake.city(),
            date_of_birth=fake.date_of_birth(minimum_age=21, maximum_age=45),
            passport_in_office=random.choice([True, False]),
        )

    def create_medical(self, candidate):
        is_fit = random.choice([True, True, False])
        CandidateMedical.objects.create(
            candidate=candidate,
            is_medically_fit=is_fit,
            remarks="" if is_fit else "Minor issues, review required",
        )

    # -----------------------------
    # Fake image generator
    # -----------------------------

    def fake_image_bytes(self):
        # simple blank jpeg bytes (no PIL dependency)
        return (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
            b"\xff\xdb\x00C\x00" + b"\x08" * 64 +
            b"\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x11\x00"
            b"\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xd2\xcf \xff\xd9"
        )
