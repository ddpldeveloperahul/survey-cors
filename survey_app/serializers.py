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

# class SurveySkyVisibilitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SurveySkyVisibility
#         fields = ["id", "obstruction_data", "multipath_risk", "emi_sources"]
#         read_only_fields = ["id", "created_at"]

class SurveySkyVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySkyVisibility
        fields = [
            "id",
            "polar_chart_image",
            "multipath_emi_source",
            "remarks",
        ]
        read_only_fields = ["id"]

    def validate(self, data):

        emi_list = data.get("multipath_emi_source", [])

        if not emi_list:
            raise serializers.ValidationError({
                "multipath_emi_source": "At least one EMI source required"
            })

        for item in emi_list:

            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    "Each EMI entry must be an object"
                )

            source = item.get("source")
            direction = item.get("direction")
            distance = item.get("distance")

            # Validate source
            if source not in EMI_SOURCE_CHOICES:
                raise serializers.ValidationError(
                    f"Invalid EMI source: {source}"
                )

            # Validate direction
            if direction is None:
                raise serializers.ValidationError(
                    f"Direction required for {source}"
                )

            if not (0 <= int(direction) <= 360):
                raise serializers.ValidationError(
                    f"Direction must be between 0-360 for {source}"
                )

            # Validate distance
            if not distance:
                raise serializers.ValidationError(
                    f"Distance required for {source}"
                )

            # If Others → require other_text
            if source == "Others" and not item.get("other_text"):
                raise serializers.ValidationError(
                    "Provide other_text when source is Others"
                )

        return data


class SurveyPowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPower
        fields = ["id", "ac_grid", "solar_possible", "sun_hours"]
        read_only_fields = ["id", "created_at"]

# class SurveyConnectivitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SurveyConnectivity
#         fields = ["id", "gsm_4g", "broadband","fiber","remarks"]
#         read_only_fields = ["id", "created_at"]



PROVIDER_CHOICES = [
    "Airtel",
    "Vodafone Idea",
    "JIO",
    "BSNL",
    "Others",
]

class SurveyConnectivitySerializer(serializers.ModelSerializer):

    def validate(self, data):
        fields = [
            ("gsm_4g", "others_gsm_4g"),
            ("broadband", "others_broadband"),
            ("fiber", "others_fiber"),
        ]

        # 🚫 EMPTY POST
        if not data:
            raise serializers.ValidationError({
                "gsm_4g": ["This field is required"],
                "broadband": ["This field is required"],
                "fiber": ["This field is required"],
            })

        # 🚫 AT LEAST ONE REQUIRED
        if not any(data.get(f[0]) for f in fields):
            errors = {}
            for field, _ in fields:
                errors[field] = ["Select at least one provider"]
            raise serializers.ValidationError(errors)

        for field, other_field in fields:
            providers = data.get(field, [])

            # Provider list validation
            if providers:
                if not isinstance(providers, list):
                    raise serializers.ValidationError({
                        field: ["Must be a list"]
                    })

                invalid = [p for p in providers if p not in PROVIDER_CHOICES]
                if invalid:
                    raise serializers.ValidationError({
                        field: [
                            f"Invalid provider(s): {invalid}. "
                            f"Allowed: {PROVIDER_CHOICES}"
                        ]
                    })

            # 🚫 "Others" selected but text missing
            if "Others" in providers and not data.get(other_field):
                raise serializers.ValidationError({
                    other_field: [
                        "Please specify the service provider name"
                    ]
                })

        return data

    class Meta:
        model = SurveyConnectivity
        fields = [
            "id",
            "gsm_4g",
            "others_gsm_4g",
            "broadband",
            "others_broadband",
            "fiber",
            "others_fiber",
            "remarks",
        ]
        read_only_fields = ["id"]


class SurveyPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPhoto
        fields =[ "id", "north_photo", "east_photo", "south_photo", "west_photo", "captured_at"]
        read_only_fields = ["id", "captured_at"]

class SurveyApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyApproval
        fields = "__all__"
