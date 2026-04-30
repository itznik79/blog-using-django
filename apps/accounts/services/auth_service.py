from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from typing import Optional, Tuple, Any, cast
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.accounts.utils.otp import generate_otp, store_otp, get_otp, delete_otp, send_otp_via_channel

User = get_user_model()


def create_user(email, password, name=None):
    if not email:
        raise ValueError("Email is required")
    if not password:
        raise ValueError("Password is required")

    email = email.strip().lower()

    try:
        with transaction.atomic():
            user_data = {"email": email}
            if name:
                user_data["name"] = name
            user = User(**user_data)
            user.set_password(password)
            user.save()
    except IntegrityError:
        raise ValueError("A user with that email already exists")

    return user


def register_user(email: str, password: str, name: Optional[str]=None):
    """Public API for registering a user."""
    return create_user(email=email, password=password, name=name)


def authenticate_user(email: str, password: str):
    """Authenticate and return user or None."""
    if not email or not password:
        return None
    # Prefer explicit check against the user model to avoid depending on custom auth backends
    email_clean = email.strip().lower()
    user = User.objects.filter(email__iexact=email_clean).first()
    if not user:
        return None
    if not user.check_password(password):
        return None
    return user


def generate_tokens_for_user(user) -> Tuple[str, str]:
    """Return (access, refresh) tokens for a user using simplejwt."""
    rt = RefreshToken.for_user(user)
    access = str(rt.access_token)
    refresh = str(rt)
    return access, refresh


def refresh_tokens(refresh_token: str) -> Tuple[str, Optional[str]]:
    """Validate refresh token and return (access, new_refresh_or_none).

    This implementation returns a fresh access token. If the blacklist/rotation
    app is enabled you may want to implement rotation and return a new refresh.
    """
    try:
        # RefreshToken expects a token-like object; cast to Any to satisfy the type checker
        rt = RefreshToken(cast(Any, refresh_token))
        access = str(rt.access_token)

        rotate = bool(settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False))
        blacklist_after = bool(settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False))

        if rotate:
            # Attempt to locate the user referenced by the refresh token
            user_id = rt.get("user_id") or rt.get("user_id")
            user = None
            if user_id is not None:
                try:
                    user = User.objects.filter(pk=user_id).first()
                except Exception:
                    user = None
            if not user:
                # If user can't be found, the token is invalid for rotation
                raise ValueError("Invalid refresh token user")

            # Issue a new refresh token for the user
            new_rt = RefreshToken.for_user(user)
            new_access = str(new_rt.access_token)

            # Blacklist the old refresh token if configured and supported
            if blacklist_after:
                try:
                    rt.blacklist()
                except AttributeError:
                    # blacklist app not installed; nothing to do
                    pass

            return new_access, str(new_rt)

        return access, None
    except TokenError:
        raise ValueError("Invalid refresh token")


def logout_refresh_token(refresh_token: str) -> None:
    """Blacklist the provided refresh token if blacklist app is enabled."""
    try:
        rt = RefreshToken(cast(Any, refresh_token))
        # If token blacklist is enabled, this will add it to the blacklist.
        rt.blacklist()
    except AttributeError:
        # blacklist not enabled; nothing to do
        return
    except TokenError:
        return


def change_password(user, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise ValueError("Old password does not match")
    user.set_password(new_password)
    user.save()


def send_otp(email: str) -> None:
    otp = generate_otp()
    try:
        store_otp(email, otp)
        send_otp_via_channel(email, otp)
    except Exception:
        # If OTP backend fails, raise a clear error so callers can handle it
        raise RuntimeError("Failed to store/send OTP")


def verify_otp(email: str, otp: str) -> bool:
    try:
        stored = get_otp(email)
    except Exception:
        return False
    if not stored:
        return False
    if stored != otp:
        return False
    # matched; delete to prevent reuse
    delete_otp(email)
    return True


def reset_password_with_otp(email: str, otp: str, new_password: str) -> None:
    if not verify_otp(email, otp):
        raise ValueError("Invalid or expired OTP")
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        raise ValueError("User not found")
    user.set_password(new_password)
    user.save()
