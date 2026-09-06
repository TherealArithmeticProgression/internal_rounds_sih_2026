import re
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import response, status, views
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FarmerProfile, OTPChallenge

PHONE_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
SUPPORTED_LANGUAGES = {"en", "hi", "pa", "bn", "ta"}


def normalize_phone(value):
    phone = str(value or "").replace(" ", "").replace("-", "")
    if not PHONE_PATTERN.fullmatch(phone):
        raise ValueError("Use an E.164 phone number, for example +919876543210.")
    return phone


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")

class RequestOTPView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_request"

    def post(self, request):
        try:
            phone = normalize_phone(request.data.get("phone_number"))
        except ValueError as error:
            return response.Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        # No fallback code is generated or returned: login must fail closed until an
        # approved server-side SMS provider adapter has been installed.
        if settings.OTP_SMS_PROVIDER == "disabled":
            return response.Response({"detail": "SMS delivery is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        now = timezone.now()
        hour_ago = now - timedelta(hours=1)
        phone_hash, ip_address = OTPChallenge.hash_phone(phone), client_ip(request)
        if OTPChallenge.objects.filter(phone_hash=phone_hash, created_at__gte=hour_ago).count() >= settings.OTP_MAX_REQUESTS_PER_PHONE_HOUR:
            return response.Response({"detail": "Too many codes requested. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        if ip_address and OTPChallenge.objects.filter(requested_ip=ip_address, created_at__gte=hour_ago).count() >= settings.OTP_MAX_REQUESTS_PER_IP_HOUR:
            return response.Response({"detail": "Too many requests from this network. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return response.Response({"detail": "SMS provider adapter has not been installed."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class VerifyOTPView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

    @transaction.atomic
    def post(self, request):
        try:
            phone = normalize_phone(request.data.get("phone_number"))
        except ValueError as error:
            return response.Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        code, language = str(request.data.get("otp", "")), request.data.get("language", "en")
        if not re.fullmatch(r"\d{6}", code) or language not in SUPPORTED_LANGUAGES:
            return response.Response({"detail": "Invalid verification request."}, status=status.HTTP_400_BAD_REQUEST)
        challenge = OTPChallenge.objects.select_for_update().filter(phone_hash=OTPChallenge.hash_phone(phone), consumed_at__isnull=True, expires_at__gt=timezone.now()).order_by("-created_at").first()
        if not challenge or challenge.attempts >= settings.OTP_MAX_ATTEMPTS:
            return response.Response({"detail": "Code expired or invalid. Request a new code."}, status=status.HTTP_400_BAD_REQUEST)
        challenge.attempts += 1
        if not check_password(code, challenge.otp_hash):
            challenge.save(update_fields=["attempts"])
            return response.Response({"detail": "Code expired or invalid."}, status=status.HTTP_400_BAD_REQUEST)
        challenge.consumed_at = timezone.now()
        challenge.save(update_fields=["attempts", "consumed_at"])

        user, created = User.objects.get_or_create(username=phone)
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        profile, p_created = FarmerProfile.objects.get_or_create(
            user=user, defaults={'phone_number': phone, 'preferred_language': language}
        )
        
        if not p_created and profile.preferred_language != language:
            profile.preferred_language = language
            profile.save(update_fields=["preferred_language"])

        refresh = RefreshToken.for_user(user)
        
        result = response.Response({
            'access': str(refresh.access_token),
            'user_id': user.id,
            'phone_number': phone,
            'language': profile.preferred_language
        })
        result.set_cookie('cropguard_refresh', str(refresh), httponly=True, secure=settings.AUTH_COOKIE_SECURE, samesite=settings.AUTH_COOKIE_SAMESITE, max_age=int(refresh.lifetime.total_seconds()), path='/api/auth/')
        return result
