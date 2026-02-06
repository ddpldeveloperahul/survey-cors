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
    site_name = models.CharField(max_length=150)
    surveyor = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="DRAFT")
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name


class SurveySubSite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey,related_name="subsites",on_delete=models.CASCADE)
    subsite_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subsite_name

class SurveyLocation(models.Model):
    survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Location for {self.survey.subsite_name}"


class SurveyMonument(models.Model):
    MONUMENT_TYPE = [("GROUND", "Ground"), ("ROOFTOP", "Rooftop")]

    survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
    monument_type = models.CharField(max_length=10, choices=MONUMENT_TYPE)
    building_stories = models.IntegerField(null=True, blank=True)
    accessibility = models.TextField()
    surroundings = models.TextField()
    
    def  __str__(self):
        return f"Monument for {self.survey.subsite_name}"

    
    
class SurveySkyVisibility(models.Model):
    survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
    obstruction_data = models.JSONField(help_text="add the lan,long and vertical angel obstruction data here")
    multipath_risk = models.BooleanField()
    emi_sources = models.TextField()
    
    def __str__(self):
        return f"Sky Visibility for {self.survey.subsite_name}"



class SurveyPower(models.Model):
    survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
    ac_grid = models.BooleanField()
    solar_possible = models.BooleanField()
    sun_hours = models.IntegerField()
    
    def __str__(self):
        return f"Power Details for {self.survey.subsite_name}"



class SurveyConnectivity(models.Model):
    survey = models.OneToOneField(SurveySubSite, on_delete=models.CASCADE)
    gsm_4g = models.BooleanField()
    broadband = models.BooleanField()
    fiber = models.BooleanField()
    remarks = models.TextField(blank=True)
    def __str__(self):
        return f"Connectivity Details for {self.survey.subsite_name}"           



# class SurveyPhoto(models.Model):
#     DIRECTION = [
#         ("NORTH", "North"),
#         ("EAST", "East"),
#         ("SOUTH", "South"),
#         ("WEST", "West"),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     sub_site = models.ForeignKey(SurveySubSite,on_delete=models.CASCADE,null=True,blank=True)
#     # direction = models.CharField(max_length=10, choices=DIRECTION)
#     north_photo = models.ImageField(upload_to="survey_photos/", null=True, blank=True)
#     east_photo = models.ImageField(upload_to="survey_photos/", null=True, blank=True)
#     south_photo = models.ImageField(upload_to="survey_photos/", null=True, blank=True)
#     west_photo = models.ImageField(upload_to="survey_photos/", null=True, blank=True)
#     # image = models.ImageField(upload_to="survey_photos/")
#     captured_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"Photos of {self.sub_site.subsite_name}"


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

    DECISION = [("APPROVED", "Approved"), ("REJECTED", "Rejected")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    approval_level = models.IntegerField(choices=LEVEL_CHOICES)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    decision = models.CharField(max_length=10, choices=DECISION)
    remarks = models.TextField()
    approved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.survey.site_name} - Level {self.approval_level} - {self.decision}"
