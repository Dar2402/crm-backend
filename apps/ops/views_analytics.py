from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from apps.bookings.models import StageHistory
from django.db.models.functions import Lead

from apps.bookings.models import Booking, ApplicationStage
from .permissions import IsStaff


class FunnelAnalyticsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        stages = ApplicationStage.objects.order_by("order")

        data = []
        for stage in stages:
            count = Booking.objects.filter(current_stage=stage).count()
            data.append({
                "stage_id": stage.id,
                "stage": stage.name,
                "count": count,
            })

        return Response(data)



class AvgStageTimeView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        data = []

        histories = (
            StageHistory.objects
            .select_related("stage")
            .order_by("booking_id", "updated_at")
        )

        # compute deltas in python (safe + DB independent)
        stage_times = {}

        last = {}

        for h in histories:
            key = (h.booking_id,)

            if key in last:
                delta = h.updated_at - last[key]["time"]
                stage = last[key]["stage"]

                stage_times.setdefault(stage, []).append(delta.total_seconds() / 86400)

            last[key] = {"time": h.updated_at, "stage": h.stage.name}

        for stage, days in stage_times.items():
            data.append({
                "stage": stage,
                "avg_days": round(sum(days) / len(days), 2),
                "samples": len(days),
            })

        return Response(data)



class TimeToDeployView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        completed = Booking.objects.filter(status="completed")

        durations = []

        for b in completed:
            first = b.stage_history.order_by("updated_at").first()
            last = b.stage_history.order_by("-updated_at").first()

            if first and last:
                durations.append((last.updated_at - first.updated_at).total_seconds() / 86400)

        if not durations:
            return Response({"avg_days": 0, "samples": 0})

        return Response({
            "avg_days": round(sum(durations) / len(durations), 2),
            "samples": len(durations),
        })



