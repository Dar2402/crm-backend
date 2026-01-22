import razorpay
import hmac, hashlib

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.conf import settings
from django.shortcuts import get_object_or_404

from apps.candidates.models import Candidate
from apps.bookings.models import Booking, ApplicationStage, StageHistory
from .models import Payment
from .serializers import CreateOrderSerializer


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class CreatePaymentOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        candidate = get_object_or_404(
            Candidate,
            id=serializer.validated_data["candidate_id"],
            status="available",
        )

        amount = candidate.price_sar * 100

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
        })

        Payment.objects.create(
            user=request.user,
            candidate=candidate,
            amount=amount,
            razorpay_order_id=order["id"],
        )

        return Response({
            "razorpay_order_id": order["id"],
            "amount": amount,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
        })



class RazorpayWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def confirm_booking(self, order_id, payment_id):
        try:
            payment = Payment.objects.select_related("candidate", "user").get(
                razorpay_order_id=order_id,
                status="created",
            )
        except Payment.DoesNotExist:
            return

        payment.status = "paid"
        payment.razorpay_payment_id = payment_id
        payment.save()

        first_stage = ApplicationStage.objects.order_by("order").first()

        booking = Booking.objects.create(
            user=payment.user,
            candidate=payment.candidate,
            current_stage=first_stage,
        )

        if first_stage:
            StageHistory.objects.create(
                booking=booking,
                stage=first_stage,
                remarks="Payment received, application created",
            )

        payment.candidate.status = "booked"
        payment.candidate.save(update_fields=["status"])


    def post(self, request):
        body = request.body
        received_sig = request.headers.get("X-Razorpay-Signature")

        expected_sig = hmac.new(
            bytes(settings.RAZORPAY_WEBHOOK_SECRET, "utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(received_sig, expected_sig):
            return Response(status=400)

        payload = request.data
        event = payload.get("event")

        if event == "payment.captured":
            payment_entity = payload["payload"]["payment"]["entity"]

            order_id = payment_entity["order_id"]
            payment_id = payment_entity["id"]

            self.confirm_booking(order_id, payment_id)

        return Response({"status": "ok"})



