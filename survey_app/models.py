import uuid
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


# class UserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("Email is required")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         return self.create_user(email, password, **extra_fields)


# class User(AbstractBaseUser, PermissionsMixin):
#     ROLE_CHOICES = [
#         ("SURVEYOR", "Surveyor"),
#         ("SUPERVISOR", "Supervisor"),
#         ("DIRECTOR", "Director"),
#         ("ZONAL_CHIEF", "Zonal Chief"),
#         ("GNRB", "GNRB Authority"),
#         ("ADMIN", "Admin"),
#     ]

#     ZONE_CHOICES = [
#         ("NORTH", "North"),
#         ("SOUTH", "South"),
#         ("EAST", "East"),
#         ("WEST", "West"),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     mobile = models.CharField(max_length=15)
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)
#     zone = models.CharField(max_length=20, choices=ZONE_CHOICES, null=True, blank=True)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     objects = UserManager()

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["name"]

#     def __str__(self):
#         return self.email

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ("SURVEYOR", "Surveyor"),
        ("SUPERVISOR", "Supervisor"),
        ("DIRECTOR", "Director"),
        ("ZONAL_CHIEF", "Zonal Chief"),
        ("GNRB", "GNRB Authority"),
        ("ADMIN", "Admin"),
    ]

    ZONE_CHOICES = [
        ("NORTH", "North"),
        ("SOUTH", "South"),
        ("EAST", "East"),
        ("WEST", "West"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # keep username for login
    username = models.CharField(max_length=150,unique=True)

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):
        return f"{self.username} ({self.role})"



# ------------------------
# STATE MODEL
# ------------------------

class State(models.Model):
    name = models.CharField(max_length=150, unique=True)

    # Latitude & Longitude added
    

    def __str__(self):
        return self.name

class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    class Meta:
        unique_together = ("state", "name")

    def __str__(self):
        return self.name

class SubDistrict(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="subdistricts")
    name = models.CharField(max_length=150)

    class Meta:
        unique_together = ("district", "name")

    def __str__(self):
        return self.name
    
    
class Town(models.Model):
    subdistrict = models.ForeignKey(SubDistrict, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("subdistrict", "name")

    def __str__(self):
        return self.name




# --------------------
# Survey Master
# --------------------

class Survey(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("SUPERVISOR_APPROVED", "Supervisor Approved"),
        ("DIRECTOR_APPROVED", "Director Approved"),
        ("ZONAL_CHIEF_APPROVED", "Zonal Chief Approved"),
        ("GNRB_APPROVED", "GNRB Approved"),
        ("REJECTED", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    subdistrict = models.ForeignKey(SubDistrict, on_delete=models.CASCADE)
    station = models.ForeignKey(Town, on_delete=models.CASCADE)

    surveyor = models.ForeignKey(User, on_delete=models.CASCADE)

    # latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="DRAFT")
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.station.name} - {self.status}"

class SurveySubSite(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    survey = models.ForeignKey(
        Survey,
        related_name="subsites",
        on_delete=models.CASCADE
    )

    location = models.CharField(max_length=150)

    priority = models.IntegerField(
        default=1,
        help_text="Priority of subsite (lower number = higher priority)"
    )

    # ✅ OPTIONAL RINEX FILE
    rinex_file = models.FileField(
        upload_to="rinex_files/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "created_at"]

    def __str__(self):
        return f"{self.location} (Priority {self.priority})"


class SurveyLocation(models.Model):
    survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Location for {self.survey.location}"

class SurveyMonument(models.Model):

    MONUMENT_TYPE = [
        ("GROUND", "Ground"),
        ("ROOFTOP", "Rooftop"),
    ]

    BUILDING_STORIES = [
        ("SINGLE", "Single Story"),
        ("DOUBLE", "Double Story"),
        ("TRIPLE", "Triple Story"),
    ]

    CHECKBOX_CHOICES = [
        "Site Properly Accessible",
        "Site is clean and free from litter",
        "Site NOT in low-lying areas or flood area",
    ]

    survey = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="surveymonument"
    )

    monument_type = models.CharField(
        max_length=10,
        choices=MONUMENT_TYPE
    )

    # Only required if Rooftop
    building_stories = models.CharField(
        max_length=10,
        choices=BUILDING_STORIES,
        blank=True,
        null=True
    )

    # Checkbox list
    site_conditions = models.JSONField(
        default=list,
        blank=True
    )

    def __str__(self):
        return f"Monument for {self.survey.subsite_name}"

EMI_SOURCE_CHOICES = [
    "HT Powerline",
    "Distribution Powerline",
    "Transformer",
    "Mobile Tower",
    "Other Radio Transmitter",
    "Electric Grid Station",
    "Water body",
    "Glazed window or Surface",
    "Others",
]

DIRECTION_CHOICES = [
    "North",
    "Northeast",
    "East",
    "Southeast",
    "South",
    "Southwest",
    "West",
    "Northwest",
]


class SurveySkyVisibility(models.Model):
    survey = models.OneToOneField(
        "SurveySubSite",
        on_delete=models.CASCADE,
        related_name="surveyskyvisibility"
    )

    polar_chart_image = models.ImageField(
        upload_to="sky_visibility/",
        null=True,
        blank=True
    )

    # Each item example:
    # [
    #   {
    #     "source": "HT Powerline",
    #     "direction": "North",
    #     "approx_distance_m": 200
    #   }
    # ]
    multipath_emi_source = models.JSONField(
        default=list,
        blank=True
    )

    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Sky Visibility for {self.survey.location}"


class SurveyPower(models.Model):

    survey = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="surveypower"
    )

    ac_grid = models.BooleanField()

    # ✅ NEW FIELD
    ac_grid_distance_meter = models.IntegerField(
        null=True,
        blank=True,
        help_text="Distance of nearest AC power connection in meters"
    )

    solar_possible = models.BooleanField()

    solar_exposure_hours = models.IntegerField()

    def __str__(self):
        return f"Power Details for {self.survey.subsite_name}"



    
PROVIDER_CHOICES = [
    "Airtel",
    "Vodafone Idea",
    "JIO",
    "BSNL",
    "Others",
]


class SurveyConnectivity(models.Model):

    survey = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="surveyconnectivity"
    )

    # Existing
    gsm_4g = models.JSONField(default=list, blank=True)
    broadband = models.JSONField(default=list, blank=True)
    fiber = models.JSONField(default=list, blank=True)

    # ✅ NEW FIELD
    airfiber = models.JSONField(default=list, blank=True)

    # Others free text
    others_gsm_4g = models.CharField(max_length=255, blank=True)
    others_broadband = models.CharField(max_length=255, blank=True)
    others_fiber = models.CharField(max_length=255, blank=True)

    # ✅ NEW OTHERS FIELD
    others_airfiber = models.CharField(max_length=255, blank=True)

    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Connectivity Details for {self.survey.subsite_name}"


class SurveyPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_site = models.OneToOneField(
        SurveySubSite,
        on_delete=models.CASCADE,
        related_name="photos"
    )
    north_photo = models.ImageField(upload_to="survey_photos/" )
    east_photo = models.ImageField(upload_to="survey_photos/" )
    south_photo = models.ImageField(upload_to="survey_photos/" )
    west_photo = models.ImageField(upload_to="survey_photos/")
    captured_at = models.DateTimeField(auto_now_add=True)
    
    def  __str__(self):
        return f"Photos of {self.sub_site.subsite_name}"

class SurveyApproval(models.Model):
    LEVEL_CHOICES = [
        (1, "Supervisor"),
        (2, "Director"),
        (3, "Zonal Chief"),
        (4, "GNRB"),
    ]

    DECISION = [("APPROVED", "Approved"), 
                ("REJECTED", "Rejected")
                ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    approval_level = models.IntegerField(choices=LEVEL_CHOICES)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    decision = models.CharField(max_length=10, choices=DECISION)
    remarks = models.TextField()
    approved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.survey.site_name} - Level {self.approval_level} - {self.decision}"



class RinexFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    file = models.FileField(
        upload_to="rinex_files/",
        null=True,
        blank=True
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RINEX File {self.id}"









#dashboard models

from django.db import models


class Statedb(models.Model):
    name = models.CharField(max_length=150, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "state"

    def __str__(self):
        return self.name


class Districtdb(models.Model):
    state = models.ForeignKey(   # ✅ FIXED
        Statedb,                # 🔥 IMPORTANT FIX
        on_delete=models.CASCADE,
        related_name="districts"
    )

    name = models.CharField(max_length=150)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("state", "name")
        db_table = "district"

    def __str__(self):
        return f"{self.name} ({self.state.name})"


class Stationdb(models.Model):
    district = models.ForeignKey(
        Districtdb,              # 🔥 IMPORTANT FIX
        on_delete=models.CASCADE,
        related_name="stations"
    )

    sl_no = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("district", "name")
        db_table = "station"

    def __str__(self):
        return self.name