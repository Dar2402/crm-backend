from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from .serializers_auth import OpsLoginSerializer



class OpsLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = OpsLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        password = serializer.validated_data["password"]

        user = authenticate(request, phone=phone, password=password)

        if not user:
            return Response({"detail": "Invalid credentials"}, status=401)

        if not user.is_staff:
            return Response({"detail": "Not authorized for ops"}, status=403)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "phone": user.phone,
                "is_staff": user.is_staff,
                "is_admin": user.is_superuser,
            }
        })