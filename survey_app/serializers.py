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

# serializers.py

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "mobile",
            "role",
            "zone",
            "created_at",
        ]


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

# serializers.py



class SurveyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyLocation
        fields = ["id", "latitude", "longitude", "address", "city", "district", "state"]
        read_only_fields = ["id", "created_at"]


# class SurveyMonumentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SurveyMonument
#         fields = ["id", "monument_type", "building_stories", "accessibility", "surroundings"]
#         read_only_fields = ["id", "created_at"]



class SurveyMonumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyMonument
        fields = [
            "id",
            "monument_type",
            "building_stories",
            "site_conditions",
        ]
        read_only_fields = ["id"]

    def validate(self, data):

        monument_type = data.get("monument_type")
        building_stories = data.get("building_stories")

        # Rooftop → building_stories required
        if monument_type == "ROOFTOP" and not building_stories:
            raise serializers.ValidationError({
                "building_stories": "Building stories required for Rooftop"
            })

        # Ground → building_stories should be empty
        if monument_type == "GROUND":
            data["building_stories"] = None

        # Validate checkboxes
        allowed = [
            "Site Properly Accessible",
            "Site is clean and free from litter",
            "Site NOT in low-lying areas or flood area",
        ]

        conditions = data.get("site_conditions", [])

        invalid = [c for c in conditions if c not in allowed]
        if invalid:
            raise serializers.ValidationError({
                "site_conditions": f"Invalid value(s): {invalid}"
            })

        return data


# class SurveySkyVisibilitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SurveySkyVisibility
#         fields = ["id", "obstruction_data", "multipath_risk", "emi_sources"]
#         read_only_fields = ["id", "created_at"]

# class SurveySkyVisibilitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SurveySkyVisibility
#         fields = [
#             "id",
#             "polar_chart_image",
#             "multipath_emi_source",
#             "remarks",
#         ]
#         read_only_fields = ["id"]

#     def validate(self, data):

#         emi_list = data.get("multipath_emi_source", [])

#         if not emi_list:
#             raise serializers.ValidationError({
#                 "multipath_emi_source": "At least one EMI source required"
#             })

#         for item in emi_list:

#             if not isinstance(item, dict):
#                 raise serializers.ValidationError(
#                     "Each EMI entry must be an object"
#                 )

#             source = item.get("source")
#             direction = item.get("direction")
#             distance = item.get("distance")

#             # Validate source
#             if source not in EMI_SOURCE_CHOICES:
#                 raise serializers.ValidationError(
#                     f"Invalid EMI source: {source}"
#                 )

#             # Validate direction
#             if direction is None:
#                 raise serializers.ValidationError(
#                     f"Direction required for {source}"
#                 )

#             if not (0 <= int(direction) <= 360):
#                 raise serializers.ValidationError(
#                     f"Direction must be between 0-360 for {source}"
#                 )

#             # Validate distance
#             if not distance:
#                 raise serializers.ValidationError(
#                     f"Distance required for {source}"
#                 )

#             # If Others → require other_text
#             if source == "Others" and not item.get("other_text"):
#                 raise serializers.ValidationError(
#                     "Provide other_text when source is Others"
#                 )

#         return data

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
            distance = item.get("approx_distance_m")

            # ✅ Validate Source
            if source not in EMI_SOURCE_CHOICES:
                raise serializers.ValidationError(
                    f"Invalid EMI source: {source}"
                )

            # ✅ Validate Direction (Dropdown)
            if direction not in DIRECTION_CHOICES:
                raise serializers.ValidationError(
                    f"Direction must be one of {DIRECTION_CHOICES}"
                )

            # ✅ Validate Distance
            if distance is None:
                raise serializers.ValidationError(
                    f"Approx. Distance required for {source}"
                )

            if not isinstance(distance, int) or distance <= 0:
                raise serializers.ValidationError(
                    f"Approx. Distance must be positive integer for {source}"
                )

            # ✅ If Others → require other_text
            if source == "Others":
                if not item.get("other_text"):
                    raise serializers.ValidationError(
                        "Provide other_text when source is Others"
                    )

        return data


# class SurveyPowerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SurveyPower
#         fields = ["id", "ac_grid", "solar_possible", "sun_hours"]
#         read_only_fields = ["id", "created_at"]


class SurveyPowerSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveyPower
        fields = [
            "id",
            "ac_grid",
            "ac_grid_distance_meter",   # ✅ new field
            "solar_possible",
            "solar_exposure_hours"
        ]
        read_only_fields = ["id"]

    def validate(self, data):

        ac_grid = data.get("ac_grid")
        distance = data.get("ac_grid_distance_meter")

        # If AC grid available → distance required
        if ac_grid:
            if distance is None:
                raise serializers.ValidationError({
                    "ac_grid_distance_meter": "Distance required when AC grid is available"
                })

            if int(distance) <= 0:
                raise serializers.ValidationError({
                    "ac_grid_distance_meter": "Distance must be greater than 0"
                })

        return data



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





class RinexFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = RinexFile
        fields = ["id", "file", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]

    def validate_file(self, value):
        if value and not value.name.lower().endswith(('.obs', '.nav', '.rnx')):
            raise serializers.ValidationError(
                "Only RINEX files (.obs, .nav, .rnx) are allowed"
            )
        return value



from rest_framework import serializers
from .models import Survey, SurveySubSite


# 🔹 Subsite Serializer
# class SubSiteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SurveySubSite
#         fields = [
#             "id",
#             "subsite_name",
#             "priority",
#             "created_at"
#         ]


# serializers.py



class FullSubSiteSerializer(serializers.ModelSerializer):

    location = SurveyLocationSerializer(source="surveylocation", read_only=True)
    monument = SurveyMonumentSerializer(source="surveymonument", read_only=True)
    sky_visibility = SurveySkyVisibilitySerializer(source="surveyskyvisibility", read_only=True)
    power = SurveyPowerSerializer(source="surveypower", read_only=True)
    connectivity = SurveyConnectivitySerializer(source="surveyconnectivity", read_only=True)
    photos = SurveyPhotoSerializer(read_only=True)

    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "subsite_name",
            "priority",
            "created_at",
            "location",
            "monument",
            "sky_visibility",
            "power",
            "connectivity",
            "photos",
        ]


class FullHierarchySurveySerializer(serializers.ModelSerializer):

    subsites = FullSubSiteSerializer(many=True)
    surveyor_name = serializers.CharField(source="surveyor.name", read_only=True)
    surveyor_username = serializers.CharField(source="surveyor.username", read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "site_name",
            "status",
            "remarks",
            "created_at",
            "surveyor_name",
            "surveyor_username",
            "subsites",
        ]
