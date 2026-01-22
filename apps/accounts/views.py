from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserSerializer, UserProfileUpdateSerializer
from .services.otp_service import generate_otp, store_otp, verify_otp
from .services.whatsapp_service import send_whatsapp_otp

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        if User.objects.filter(phone=phone).exists():
            return Response(
                {"detail": "User already registered. Please login."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            phone=phone,
            first_name=serializer.validated_data.get("first_name"),
            last_name=serializer.validated_data.get("last_name", ""),
            email=serializer.validated_data.get("email"),
            country_code=serializer.validated_data.get("country_code"),
            state=serializer.validated_data.get("state", ""),
            city=serializer.validated_data.get("city", ""),
            address_line1=serializer.validated_data.get("address_line1", ""),
            address_line2=serializer.validated_data.get("address_line2", ""),
            postal_code=serializer.validated_data.get("postal_code", ""),
            is_active=True,
        )

        return Response(
            {"detail": "Registration successful. Please login with OTP."},
            status=status.HTTP_201_CREATED,
        )

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

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not registered. Please register first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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



class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = request.user

        for field, value in serializer.validated_data.items():
            setattr(user, field, value)

        user.save()

        return Response(
            {
                "detail": "Profile updated successfully",
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "country_code": user.country_code,
                    "state": user.state,
                    "city": user.city,
                    "address_line1": user.address_line1,
                    "address_line2": user.address_line2,
                    "postal_code": user.postal_code,
                },
            }
        )

