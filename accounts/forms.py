from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
