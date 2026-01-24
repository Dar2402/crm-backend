from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import SendOTPView, VerifyOTPView, MeView, RegisterView, UpdateProfileView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("update-profile/", UpdateProfileView.as_view()),
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/", MeView.as_view()),
]
