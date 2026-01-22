import re
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


class UserSerializer(serializers.Serializer):
    phone = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True)

    country_code = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    address_line1 = serializers.CharField(required=False, allow_blank=True)
    address_line2 = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError("Phone must be in E.164 format")
        return value


class UserProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=50)
    last_name = serializers.CharField(required=False, max_length=50)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)

    country_code = serializers.CharField(required=False, max_length=2)
    state = serializers.CharField(required=False, max_length=100)
    city = serializers.CharField(required=False, max_length=100)
    address_line1 = serializers.CharField(required=False, max_length=255)
    address_line2 = serializers.CharField(required=False, max_length=255)
    postal_code = serializers.CharField(required=False, max_length=20)

    def validate_country_code(self, value):
        if value and not re.match(r"^[A-Z]{2}$", value.upper()):
            raise serializers.ValidationError("Country code must be ISO-2 format (e.g. IN, SA)")
        return value.upper()

    def validate_postal_code(self, value):
        if value and len(value) < 4:
            raise serializers.ValidationError("Postal code looks too short")
        return value


