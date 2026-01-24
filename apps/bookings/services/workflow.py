from apps.bookings.models import Booking, StageHistory, ApplicationStage
from apps.candidates.models import Candidate
from django.core.exceptions import ValidationError
from django.db import transaction


class BookingWorkflowService:
    """
    Single source of truth for:
    - Booking lifecycle
    - Candidate status transitions
    """

    # -------------------------
    # Booking creation
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_booking(user, candidate_id):
        candidate = (
            Candidate.objects
            .select_for_update()
            .filter(id=candidate_id)
            .first()
        )

        if not candidate:
            raise ValidationError("Candidate not found")

        if candidate.status != "available":
            raise ValidationError("Candidate is no longer available")

        if Booking.objects.filter(
                candidate=candidate,
                status="active"
        ).exists():
            raise ValidationError("Candidate already booked")

        first_stage = ApplicationStage.objects.order_by("order").first()
        if not first_stage:
            raise ValidationError("No application stages configured")

        booking = Booking.objects.create(
            user=user,
            candidate=candidate,
            current_stage=first_stage,
            status="active",
        )

        StageHistory.objects.create(
            booking=booking,
            stage=first_stage,
            remarks="Application submitted",
        )

        candidate.status = "booked"
        candidate.save(update_fields=["status"])

        return booking

    # -------------------------
    # Stage movement
    # -------------------------
    @staticmethod
    @transaction.atomic
    def move_stage(booking, new_stage, remarks="Stage updated"):
        old_stage = booking.current_stage

        if old_stage and new_stage.order <= old_stage.order:
            raise ValidationError("Cannot move to same or previous stage")

        booking.current_stage = new_stage
        booking.save(update_fields=["current_stage"])

        StageHistory.objects.create(
            booking=booking,
            stage=new_stage,
            remarks=remarks,
        )

        # Candidate sync rules
        stage_name = new_stage.name.lower()

        if stage_name == "medical":
            booking.candidate.status = "booked"

        elif stage_name == "deployed":
            booking.candidate.status = "deployed"
            booking.status = "completed"

        booking.candidate.save(update_fields=["status"])
        booking.save(update_fields=["status"])

        return booking

    # -------------------------
    # Reject booking
    # -------------------------
    @staticmethod
    @transaction.atomic
    def reject_booking(booking, remarks="Booking rejected"):
        if booking.status != "active":
            raise ValidationError("Only active bookings can be rejected")

        booking.status = "rejected"
        booking.save(update_fields=["status"])

        StageHistory.objects.create(
            booking=booking,
            stage=booking.current_stage,
            remarks=remarks,
        )

        booking.candidate.status = "available"
        booking.candidate.save(update_fields=["status"])

        return booking

    # -------------------------
    # Deploy booking
    # -------------------------
    @staticmethod
    @transaction.atomic
    def deploy_booking(booking, remarks="Candidate deployed"):
        if booking.status != "active":
            raise ValidationError("Only active bookings can be deployed")

        booking.status = "completed"
        booking.save(update_fields=["status"])

        StageHistory.objects.create(
            booking=booking,
            stage=booking.current_stage,
            remarks=remarks,
        )

        booking.candidate.status = "deployed"
        booking.candidate.save(update_fields=["status"])

        return booking
