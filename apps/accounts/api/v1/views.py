from typing import Dict, Any, cast

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle

from django.contrib.auth import get_user_model
from django.conf import settings

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    RefreshSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    MinimalUserSerializer,
)

from apps.accounts.services import auth_service

User = get_user_model()


def _safe_validated_data(serializer) -> Dict[str, Any]:
    """Return a dict for serializer.validated_data or an empty dict.

    Converts byte keys/values to str if necessary and guards against
    non-mapping validated_data (e.g., lists from ListSerializer).
    """
    raw = getattr(serializer, "validated_data", {})
    if not isinstance(raw, dict):
        return {}
    cleaned: Dict[str, Any] = {}
    for k, v in raw.items():
        key = k.decode() if isinstance(k, (bytes, bytearray)) else k
        val = v.decode() if isinstance(v, (bytes, bytearray)) else v
        cleaned[str(key)] = val
    return cast(Dict[str, Any], cleaned)


# 🚫 Rate limit login attempts
class LoginThrottle(UserRateThrottle):
    rate = "5/min"


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        # FIX: cast() tells Pylance the exact type; avoids "ListSerializer | Any | LoginSerializer" mismatch
        serializer = cast(LoginSerializer, LoginSerializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        data: Dict[str, Any] = _safe_validated_data(serializer)

        user = auth_service.authenticate_user(data["email"], data["password"])
        if not user:
            return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        access, refresh = auth_service.generate_tokens_for_user(user)

        response = Response({"message": "Login successful", "access": access}, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Strict",
            max_age=7 * 24 * 60 * 60,
        )
        return response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = cast(RegisterSerializer, RegisterSerializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        data: Dict[str, Any] = _safe_validated_data(serializer)

        user = auth_service.register_user(email=data["email"], password=data["password"], name=data.get("name", ""))

        user_data = MinimalUserSerializer(user).data
        return Response({"message": "User registered successfully", "data": user_data}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = cast(LogoutSerializer, LogoutSerializer(data=request.data))
        serializer.is_valid(raise_exception=False)
        data: Dict[str, Any] = _safe_validated_data(serializer)
        refresh = data.get("refresh") or request.COOKIES.get("refresh_token")
        if isinstance(refresh, (bytes, bytearray)):
            refresh = refresh.decode()
        if refresh:
            auth_service.logout_refresh_token(refresh)
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = cast(RefreshSerializer, RefreshSerializer(data=request.data))
        serializer.is_valid(raise_exception=False)
        data: Dict[str, Any] = _safe_validated_data(serializer)
        refresh = data.get("refresh") or request.COOKIES.get("refresh_token")
        if isinstance(refresh, (bytes, bytearray)):
            refresh = refresh.decode()
        if not refresh:
            return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            access, new_refresh = auth_service.refresh_tokens(refresh)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        response = Response({"access": access}, status=status.HTTP_200_OK)
        if new_refresh:
            response.set_cookie("refresh_token", new_refresh, httponly=True, samesite="Strict")
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = cast(ChangePasswordSerializer, ChangePasswordSerializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        pdata: Dict[str, Any] = _safe_validated_data(serializer)
        auth_service.change_password(request.user, pdata["old_password"], pdata["new_password"])
        return Response({"message": "Password changed"}, status=status.HTTP_200_OK)


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = cast(SendOTPSerializer, SendOTPSerializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        sdata: Dict[str, Any] = _safe_validated_data(serializer)
        auth_service.send_otp(sdata["email"])
        return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = cast(VerifyOTPSerializer, VerifyOTPSerializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        vdata: Dict[str, Any] = _safe_validated_data(serializer)
        ok = auth_service.verify_otp(vdata["email"], vdata["otp"])
        if not ok:
            return Response({"detail": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "OTP verified"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = cast(ResetPasswordSerializer, ResetPasswordSerializer(data=request.data))
        serializer.is_valid(raise_exception=True)
        rdata: Dict[str, Any] = _safe_validated_data(serializer)
        try:
            auth_service.reset_password_with_otp(rdata["email"], rdata["otp"], rdata["new_password"])
        except ValueError:
            return Response({"detail": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Password reset"}, status=status.HTTP_200_OK)
