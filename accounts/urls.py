from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify-email/", views.verify_email_otp_view, name="verify_email_otp"),
    path("resend-email/", views.resend_email_otp_view, name="resend_email_otp"),
    path("profile/setup/", views.profile_setup_view, name="profile_setup"),

]
