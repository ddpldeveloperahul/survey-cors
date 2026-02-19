from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import Survey, User


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


from django import forms
from .models import Survey, District, SubDistrict, Town


# class SurveyForm(forms.ModelForm):

#     class Meta:
#         model = Survey
#         fields = [
#             "state",
#             "district",
#             "subdistrict",
#             "station",
#             "remarks",
#         ]

#         widgets = {
#             "state": forms.Select(attrs={"class": "form-control"}),
#             "district": forms.Select(attrs={"class": "form-control"}),
#             "subdistrict": forms.Select(attrs={"class": "form-control"}),
#             "station": forms.Select(attrs={"class": "form-control"}),
#             "remarks": forms.Textarea(attrs={
#                 "class": "form-control",
#                 "rows": 3
#             }),
#         }

class SurveyForm(forms.ModelForm):

    class Meta:
        model = Survey
        fields = [
            "state",
            "district",
            "subdistrict",
            "station",
            "remarks",
        ]

        widgets = {
            "state": forms.Select(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control"}),
            "subdistrict": forms.Select(attrs={"class": "form-control"}),
            "station": forms.Select(attrs={"class": "form-control"}),
            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Initially empty
        self.fields["district"].queryset = District.objects.none()
        self.fields["subdistrict"].queryset = SubDistrict.objects.none()
        self.fields["station"].queryset = Town.objects.none()

        # 🔹 If State Selected
        if "state" in self.data:
            try:
                state_id = int(self.data.get("state"))
                self.fields["district"].queryset = District.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                pass

        # 🔹 If District Selected
        if "district" in self.data:
            try:
                district_id = int(self.data.get("district"))
                self.fields["subdistrict"].queryset = SubDistrict.objects.filter(district_id=district_id)
            except (ValueError, TypeError):
                pass

        # 🔹 If SubDistrict Selected
        if "subdistrict" in self.data:
            try:
                subdistrict_id = int(self.data.get("subdistrict"))
                self.fields["station"].queryset = Town.objects.filter(subdistrict_id=subdistrict_id)
            except (ValueError, TypeError):
                pass

