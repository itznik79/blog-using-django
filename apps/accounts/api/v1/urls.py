from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    RefreshView,
    LogoutView,
    ChangePasswordView,
    SendOTPView,
    VerifyOTPView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
]