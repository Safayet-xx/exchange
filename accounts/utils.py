from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import urljoin

def email_domain_allowed(email: str) -> bool:
    allowed = getattr(settings, "ALLOWED_UNI_DOMAINS", set())
    if not allowed:
        return True
    try:
        domain = email.split("@", 1)[1].lower()
    except Exception:
        return False
    return domain in allowed

def send_otp_email(user, otp_obj, request=None):
    subject = "Your Exchange verification code"
    msg = (f"Hi,\n\nYour verification code is: {otp_obj.code}\n"
           f"This code expires in {getattr(settings, 'OTP_EXP_MINUTES', 10)} minutes.\n\n"
           "If you did not request this, you can ignore this email.")
    send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
