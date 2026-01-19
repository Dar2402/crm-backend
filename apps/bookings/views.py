from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import Booking, ApplicationStage, StageHistory
from apps.candidates.models import Candidate
from .serializers import BookingCreateSerializer, BookingListSerializer, StageHistorySerializer


class CreateBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        candidate_id = serializer.validated_data["candidate_id"]
        candidate = get_object_or_404(Candidate, id=candidate_id, status="available")

        # prevent duplicate active booking
        if Booking.objects.filter(user=request.user, candidate=candidate, status="active").exists():
            return Response(
                {"detail": "Already booked this candidate"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        first_stage = ApplicationStage.objects.order_by("order").first()

        booking = Booking.objects.create(
            user=request.user,
            candidate=candidate,
            current_stage=first_stage,
        )

        if first_stage:
            StageHistory.objects.create(
                booking=booking,
                stage=first_stage,
                remarks="Application submitted",
            )

        candidate.status = "booked"
        candidate.save(update_fields=["status"])

        return Response({"detail": "Booking created", "booking_id": booking.id})


class MyBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Booking.objects.filter(user=request.user).select_related(
            "candidate", "current_stage"
        )

        data = BookingListSerializer(qs, many=True).data
        return Response(data)


class BookingTimelineView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        booking = get_object_or_404(Booking, id=pk, user=request.user)

        history = booking.stage_history.select_related("stage").order_by("updated_at")
        data = StageHistorySerializer(history, many=True).data
        return Response(data)
