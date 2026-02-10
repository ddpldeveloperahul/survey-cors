from rest_framework import serializers # type: ignore
from .models import *

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "name",
            "email",
            "mobile",
            "role",
            "zone",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # 🔑 CREATE TOKEN
        Token.objects.create(user=user)

        return user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"]
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        data["user"] = user
        return data



class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"
        read_only_fields = ("surveyor", "status")
        
class SurveySubSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "survey",        # ✅ ADD THIS
            "subsite_name",
            "priority",
            "created_at",
        ]
        read_only_fields = ["id", "survey", "created_at"]


class SurveyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyLocation
        fields = ["id", "latitude", "longitude", "address", "city", "district", "state"]
        read_only_fields = ["id", "created_at"]


class SurveyMonumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyMonument
        fields = ["id", "monument_type", "building_stories", "accessibility", "surroundings"]
        read_only_fields = ["id", "created_at"]

class SurveySkyVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySkyVisibility
        fields = ["id", "obstruction_data", "multipath_risk", "emi_sources"]
        read_only_fields = ["id", "created_at"]

class SurveyPowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPower
        fields = ["id", "ac_grid", "solar_possible", "sun_hours"]
        read_only_fields = ["id", "created_at"]

class SurveyConnectivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyConnectivity
        fields = ["id", "gsm_4g", "broadband","fiber","remarks"]
        read_only_fields = ["id", "created_at"]

class SurveyPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPhoto
        fields =[ "id", "north_photo", "east_photo", "south_photo", "west_photo", "captured_at"]
        read_only_fields = ["id", "captured_at"]

class SurveyApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyApproval
        fields = "__all__"
