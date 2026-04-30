from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers

User = get_user_model()


class MinimalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "email", "name")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value.lower()

    def create(self, validated_data: Dict[str, Any]) -> AbstractBaseUser:
        # Service layer will actually persist; serializer only builds data
        return User(email=validated_data["email"], name=validated_data.get("name", ""))


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # minimal validation; service handles authentication
        data["email"] = data["email"].lower()
        return data


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

