from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .utils import email_domain_allowed

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email_domain_allowed(email):
            raise forms.ValidationError("Please use your university email address.")
        return email

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class OTPForm(forms.Form):
    code = forms.CharField(
        label="Verification code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"autocomplete": "one-time-code", "inputmode": "numeric"}),
    )
from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "university", "course", "year_of_study", "phone", "bio", "avatar", "skills"]
