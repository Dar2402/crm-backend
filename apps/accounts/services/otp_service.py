import random
import hashlib
from datetime import timedelta

from django.utils import timezone

from ..models import PhoneOTP
from django.conf import settings


OTP_EXPIRY_MINUTES = settings.OTP_EXPIRY_MINUTES
MAX_ATTEMPTS = settings.MAX_ATTEMPTS


def generate_otp():
    return f"{random.randint(100000, 999999)}"


def _hash(otp: str):
    return hashlib.sha256(otp.encode()).hexdigest()


def store_otp(phone, otp):
    # delete old OTPs for this phone
    PhoneOTP.objects.filter(phone=phone).delete()

    PhoneOTP.objects.create(
        phone=phone,
        otp_hash=_hash(otp),
        expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )


def verify_otp(phone, otp):
    try:
        record = PhoneOTP.objects.get(phone=phone)
    except PhoneOTP.DoesNotExist:
        return False

    if record.expires_at < timezone.now():
        record.delete()
        return False

    if record.attempts >= MAX_ATTEMPTS:
        record.delete()
        return False

    if record.otp_hash != _hash(otp):
        record.attempts += 1
        record.save(update_fields=["attempts"])
        return False

    record.delete()
    return True
