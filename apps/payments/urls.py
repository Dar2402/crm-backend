from django.urls import path
from .views import CreatePaymentOrderView, RazorpayWebhookView

urlpatterns = [
    path("create-order/", CreatePaymentOrderView.as_view()),
    path("webhook/", RazorpayWebhookView.as_view()),
]
