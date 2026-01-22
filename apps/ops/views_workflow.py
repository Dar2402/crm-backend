from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.bookings.models import Booking, ApplicationStage, StageHistory
from apps.candidates.models import Candidate

from .permissions import IsStaff, IsAdmin
from .serializers import MoveStageSerializer


class MoveBookingStageView(APIView):
    permission_classes = [IsStaff]

    @transaction.atomic
    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        serializer = MoveStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_stage = get_object_or_404(
            ApplicationStage, id=serializer.validated_data["stage_id"]
        )

        old_stage = booking.current_stage

        if old_stage and new_stage.order <= old_stage.order:
            return Response(
                {"detail": "Cannot move booking to same or previous stage"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.current_stage = new_stage
        booking.save()

        StageHistory.objects.create(
            booking=booking,
            stage=new_stage,
            remarks=serializer.validated_data.get("remarks", "Stage updated by ops"),
        )

        # Candidate sync rules
        if new_stage.name.lower() == "medical":
            booking.candidate.status = "booked"
        elif new_stage.name.lower() == "deployed":
            booking.candidate.status = "deployed"
            booking.status = "completed"

        booking.candidate.save(update_fields=["status"])
        booking.save(update_fields=["status"])

        return Response({"detail": "Stage updated successfully"})


class RejectBookingView(APIView):
    permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        booking.status = "rejected"
        booking.save(update_fields=["status"])

        StageHistory.objects.create(
            booking=booking,
            stage=booking.current_stage,
            remarks="Booking rejected by admin",
        )

        booking.candidate.status = "available"
        booking.candidate.save(update_fields=["status"])

        return Response({"detail": "Booking rejected"})



class DeployBookingView(APIView):
    permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        booking.status = "completed"
        booking.save(update_fields=["status"])

        StageHistory.objects.create(
            booking=booking,
            stage=booking.current_stage,
            remarks="Candidate deployed",
        )

        booking.candidate.status = "deployed"
        booking.candidate.save(update_fields=["status"])

        return Response({"detail": "Candidate marked as deployed"})
