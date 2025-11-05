from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import SignUpForm, LoginForm, OTPForm, ProfileForm
from .utils_stytch import start_email_otp, verify_email_otp

User = get_user_model()


def signup_view(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        # mark unverified until OTP success (remove if your User has no such field)
        if not hasattr(user, "email_verified"):
            pass
        user.email_verified = False
        user.save()

        # Send OTP and capture method_id
        method_id = start_email_otp(user.email)

        # Store for verify step
        request.session["otp_uid"] = user.pk
        request.session["otp_email"] = user.email
        request.session["otp_method_id"] = method_id

        messages.success(request, f"We emailed a verification code to {user.email}.")
        return redirect("accounts:verify_email_otp")
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        # If email not verified yet, start OTP
        if not getattr(user, "email_verified", False):
            method_id = start_email_otp(user.email)
            request.session["otp_uid"] = user.pk
            request.session["otp_email"] = user.email
            request.session["otp_method_id"] = method_id
            messages.info(request, "We sent a verification code to your email.")
            return redirect("accounts:verify_email_otp")

        # Normal login
        login(request, user)

        # ➜ NEW: gate to profile setup if not completed
        profile = getattr(user, "profile", None)
        if profile is not None and not getattr(profile, "is_completed", False):
            return redirect("accounts:profile_setup")

        return redirect("home")
    return render(request, "accounts/login.html", {"form": form})


def verify_email_otp_view(request):
    uid = request.session.get("otp_uid")
    email = request.session.get("otp_email")
    method_id = request.session.get("otp_method_id")
    if not uid or not email:
        messages.error(request, "Session expired. Please sign up or log in again.")
        return redirect("accounts:login")

    form = OTPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"].strip()

        ok = verify_email_otp(code, method_id=method_id, email=email)
        if ok:
            user = User.objects.get(pk=uid)
            if hasattr(user, "email_verified"):
                user.email_verified = True
                user.save(update_fields=["email_verified"])
            login(request, user)

            # cleanup session
            for k in ("otp_uid", "otp_email", "otp_method_id"):
                request.session.pop(k, None)

            messages.success(request, "Email verified. Welcome!")

            # ➜ NEW: gate to profile setup if not completed
            profile = getattr(user, "profile", None)
            if profile is not None and not getattr(profile, "is_completed", False):
                return redirect("accounts:profile_setup")

            return redirect("home")

        messages.error(request, "Invalid or expired code. Please try again.")

    return render(request, "accounts/verify_email.html", {"form": form, "email": email})


def resend_email_otp_view(request):
    uid = request.session.get("otp_uid")
    email = request.session.get("otp_email")
    if not uid or not email:
        messages.error(request, "Nothing to resend. Please start again.")
        return redirect("accounts:login")

    method_id = start_email_otp(email)  # fresh code; capture a new method_id
    request.session["otp_method_id"] = method_id

    messages.success(request, f"A new code was sent to {email}.")
    return redirect("accounts:verify_email_otp")


@login_required
def profile_setup_view(request):
    """
    Force first-time users to complete their profile before accessing the site.
    Assumes a Profile object is auto-created by a post_save signal.
    """
    # Get or create profile safely (avoids attribute errors if signal not yet added)
    profile = getattr(request.user, "profile", None)
    if profile is None:
        from .models import Profile  # local import to avoid circulars on module import
        profile, _ = Profile.objects.get_or_create(user=request.user)

    if getattr(profile, "is_completed", False):
        return redirect("home")

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            profile.is_completed = True
            profile.save(update_fields=["is_completed"])
            return redirect("home")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_setup.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You are logged out.")
    return redirect("accounts:login")
