from twilio.rest import Client
from django.conf import settings

client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN,
)


def send_whatsapp_otp(phone, otp):
    body = f"Your login OTP is: {otp}. Valid for 5 minutes."

    client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=f"whatsapp:{phone}",
        body=body,
    )
