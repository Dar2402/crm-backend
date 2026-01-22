import csv
from django.http import HttpResponse

from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.models import User
from apps.candidates.models import Candidate
from apps.bookings.models import Booking, ApplicationStage

from .permissions import IsStaff


class DashboardSummaryView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        data = {
            "users": User.objects.count(),
            "candidates": Candidate.objects.count(),
            "available_candidates": Candidate.objects.filter(status="available").count(),
            "booked_candidates": Candidate.objects.filter(status="booked").count(),
            "deployed_candidates": Candidate.objects.filter(status="deployed").count(),
            "total_bookings": Booking.objects.count(),
        }
        return Response(data)


class BookingsByStageView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        qs = Booking.objects.values(
            "current_stage__name"
        ).annotate(count=Count("id")).order_by()

        return Response(qs)


class BookingTrendView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        start = timezone.now() - timedelta(days=14)

        qs = (
            Booking.objects.filter(created_at__gte=start)
            .extra(select={"day": "date(created_at)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        return Response(qs)


class OpsBookingsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        qs = Booking.objects.select_related("user", "candidate", "current_stage")

        data = []
        for b in qs:
            data.append({
                "id": b.id,
                "user": b.user.phone,
                "candidate": b.candidate.full_name,
                "stage": b.current_stage.name if b.current_stage else None,
                "status": b.status,
                "created_at": b.created_at,
            })

        return Response(data)


class OpsCandidatesView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        qs = Candidate.objects.all()

        data = list(qs.values(
            "id", "full_name", "nationality", "applied_for", "status", "price_sar"
        ))

        return Response(data)


class ExportBookingsCSV(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="bookings.csv"'

        writer = csv.writer(response)
        writer.writerow(["ID", "User", "Candidate", "Stage", "Status", "Created At"])

        for b in Booking.objects.select_related("user", "candidate", "current_stage"):
            writer.writerow([
                b.id,
                b.user.phone,
                b.candidate.full_name,
                b.current_stage.name if b.current_stage else "",
                b.status,
                b.created_at,
            ])

        return response

