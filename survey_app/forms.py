from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User


# -------------------------
# SIGNUP FORM (ALL FIELDS)
# -------------------------
class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "email",
            "mobile",
            "role",
            "zone",
            "password1",
            "password2",
        ]

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if not mobile.isdigit() or len(mobile) != 10:
            raise forms.ValidationError("Enter valid 10 digit mobile number")
        return mobile
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })


# -------------------------
# LOGIN FORM (USERNAME + PASSWORD ONLY)
# -------------------------
class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Username"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username or password")

        cleaned_data["user"] = user
        return cleaned_data
