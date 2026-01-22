from rest_framework import serializers


class MoveStageSerializer(serializers.Serializer):
    stage_id = serializers.IntegerField()
    remarks = serializers.CharField(required=False, allow_blank=True)
