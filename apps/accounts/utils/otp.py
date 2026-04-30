import random
import logging
from typing import Optional

from django.conf import settings
import redis

logger = logging.getLogger(__name__)


def _get_redis_client():
    url = getattr(settings, "REDIS_URL", "redis://redis:6379/0")
    return redis.from_url(url)


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP of given length."""
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return str(random.randint(start, end))


def store_otp(email: str, otp: str, ttl: int = 300) -> None:
    client = _get_redis_client()
    key = f"otp:{email.lower()}"
    client.setex(key, ttl, otp)


def get_otp(email: str) -> Optional[str]:
    client = _get_redis_client()
    key = f"otp:{email.lower()}"
    value = client.get(key)
    return value.decode() if value else None


def delete_otp(email: str) -> None:
    client = _get_redis_client()
    key = f"otp:{email.lower()}"
    client.delete(key)


def send_otp_via_channel(email: str, otp: str) -> None:
    # Placeholder for sending OTP: email/SMS provider integration.
    logger.info("Send OTP to %s: %s", email, otp)
