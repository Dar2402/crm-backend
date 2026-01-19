from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .services.otp_service import generate_otp, store_otp, verify_otp
from .services.whatsapp_service import send_whatsapp_otp

User = get_user_model()


class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        otp = generate_otp()
        store_otp(phone, otp)

        try:
            send_whatsapp_otp(phone, otp)
        except Exception as e:
            return Response(
                {"detail": "Failed to send OTP", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"detail": "OTP sent"})


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        if not verify_otp(phone, code):
            return Response(
                {"detail": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, _ = User.objects.get_or_create(phone=phone)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })


class MeView(APIView):
    def get(self, request):
        u = request.user
        return Response({
            "id": u.id,
            "phone": u.phone,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "country_code": u.country_code,
            "city": u.city,
        })
