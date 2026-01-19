from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError("Phone must be in E.164 format (+countrycode...)")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)
