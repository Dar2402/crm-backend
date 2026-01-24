from apps.candidates.models import Candidate
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking
from .serializers import BookingCreateSerializer, BookingListSerializer, StageHistorySerializer
from .services.workflow import BookingWorkflowService


class CreateBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            booking = BookingWorkflowService.create_booking(
                user=request.user,
                candidate_id=serializer.validated_data["candidate_id"],
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Booking created", "booking_id": booking.id},
            status=status.HTTP_201_CREATED,
        )


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
