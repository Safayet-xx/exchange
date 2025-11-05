# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    """
    If a user is authenticated but profile is not completed, force redirect to profile setup,
    except for allowed routes and static/media paths.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Names of routes we allow even if profile incomplete
        self.allowed_names = {
            "accounts:profile_setup",
            "accounts:logout",
            "accounts:verify_email_otp",
            "accounts:resend_email_otp",
            "accounts:login",
            "accounts:signup",
            "admin:index",
        }

    def __call__(self, request):
        user = getattr(request, "user", None)

        # Allow static/media
        path = request.path
        if path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)

        if user and user.is_authenticated:
            # Try to reverse the setup URL once to avoid loops
            try:
                setup_url = reverse("accounts:profile_setup")
            except Exception:
                setup_url = "/accounts/profile/setup/"

            # Allow the setup path itself
            if path == setup_url:
                return self.get_response(request)

            # Gate if profile exists but not completed
            profile = getattr(user, "profile", None)
            if profile is not None and not getattr(profile, "is_completed", False):
                return redirect(setup_url)

        return self.get_response(request)
