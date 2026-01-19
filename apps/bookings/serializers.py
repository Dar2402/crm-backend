from rest_framework import serializers
from .models import Booking, StageHistory, ApplicationStage


class BookingCreateSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStage
        fields = ["id", "name", "order"]


class StageHistorySerializer(serializers.ModelSerializer):
    stage = StageSerializer()

    class Meta:
        model = StageHistory
        fields = ["stage", "updated_at", "remarks"]


class BookingListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source="candidate.full_name")
    current_stage = StageSerializer()

    class Meta:
        model = Booking
        fields = ["id", "candidate_name", "current_stage", "status", "created_at"]
