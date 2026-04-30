from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

User = get_user_model()


def get_user_by_email(email: str) -> Optional[AbstractBaseUser]:
    """Return a user by email or None. Uses case-insensitive lookup."""
    if not email:
        return None
    try:
        return User.objects.get(email__iexact=email.strip().lower())
    except User.DoesNotExist:
        return None


def get_user_by_id(user_id: int) -> Optional[AbstractBaseUser]:
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None
