from apps.bookings.models import Booking, ApplicationStage, StageHistory
from apps.bookings.services.workflow import BookingWorkflowService
from apps.candidates.models import Candidate
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsStaff, IsAdmin
from .serializers import MoveStageSerializer


class MoveBookingStageView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        serializer = MoveStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_stage = get_object_or_404(
            ApplicationStage,
            id=serializer.validated_data["stage_id"],
        )

        try:
            BookingWorkflowService.move_stage(
                booking=booking,
                new_stage=new_stage,
                remarks=serializer.validated_data.get("remarks", "Stage updated by ops"),
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Stage updated successfully"})


class RejectBookingView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        try:
            BookingWorkflowService.reject_booking(
                booking,
                remarks="Booking rejected by admin",
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Booking rejected"})


class DeployBookingView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)

        try:
            BookingWorkflowService.deploy_booking(
                booking,
                remarks="Candidate deployed",
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Candidate marked as deployed"})
