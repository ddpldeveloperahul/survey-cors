from rest_framework import serializers # type: ignore
from .models import *

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User
from rest_framework import serializers
from .models import User, PasswordResetOTP


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # ✅ Password match check
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        return data
# class SignupSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = [
#             "username",
#             "password",
#             "name",
#             "email",
#             "mobile",
#             "role",
#             "zone",
#         ]

#     def create(self, validated_data):
#         password = validated_data.pop("password")
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()

#         # 🔑 CREATE TOKEN
#         Token.objects.create(user=user)

#         return user


from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User


from rest_framework import serializers
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

        role = validated_data.get("role")

        user = User(**validated_data)
        user.set_password(password)

        # 🔑 Director automatically approved
        if role == "DIRECTOR":
            user.is_approved = True
        else:
            user.is_approved = False

        user.save()

        Token.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):

        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_approved:
            raise serializers.ValidationError("Account not approved yet")

        data["user"] = user

        return data
# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(
#             username=data["username"],
#             password=data["password"]
#         )
#         if not user:
#             raise serializers.ValidationError("Invalid username or password")
#         data["user"] = user
#         return data

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(
#             username=data["username"],
#             password=data["password"]
#         )

#         if not user:
#             raise serializers.ValidationError("Invalid username or password")

#         if not user.is_approved:
#             raise serializers.ValidationError("Account not approved yet")

#         data["user"] = user
#         return data

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

    state_name = serializers.CharField(source="state.name", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    subdistrict_name = serializers.CharField(source="subdistrict.name", read_only=True)
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "state",
            "state_name",
            "district",
            "district_name",
            "subdistrict",
            "subdistrict_name",
            "station",
            "station_name",
            "status",
            "remarks",
            "created_at",
        ]
        read_only_fields = ("surveyor", "status", "created_at")
        
class SurveySubSiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "survey",
            "location",
            "priority",
            "rinex_file",
            "contact_details",
            "created_at",
        ]
        read_only_fields = ["id", "survey", "created_at"]
        extra_kwargs = {
            "location": {"required": True},
            "priority": {"required": True},
        }

    # ✅ RINEX FILE VALIDATION (Optional)
    def validate_rinex_file(self, value):
        if value and not value.name.lower().endswith(('.obs', '.nav', '.rnx')):
            raise serializers.ValidationError(
                "Only RINEX files (.obs, .nav, .rnx) are allowed"
            )
        return value

    def validate(self, data):

        survey = self.context.get("survey")
        instance = getattr(self, "instance", None)

        if not data.get("location"):
            raise serializers.ValidationError({
                "location": "This field is required."
            })

        # ✅ Duplicate Location Check
        if SurveySubSite.objects.filter(
            survey=survey,
            location=data.get("location")
        ).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({
                "location": "Location already exists in this survey."
            })

        # ✅ Duplicate Priority Check
        if SurveySubSite.objects.filter(
            survey=survey,
            priority=data.get("priority")
        ).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({
                "priority": "Priority already exists in this survey."
            })

        return data




class SurveyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyLocation
        fields = ["id", "latitude", "longitude", "address", "city", "district", "state"]
        read_only_fields = ["id", "created_at"]

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
            distance = item.get("approx_distance_meter")

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
            ("airfiber", "others_airfiber"),   # ✅ Added
        ]

        if not data:
            raise serializers.ValidationError({
                field: ["This field is required"]
                for field, _ in fields
            })

        # At least one provider required
        if not any(data.get(field) for field, _ in fields):
            raise serializers.ValidationError({
                field: ["Select at least one provider"]
                for field, _ in fields
            })

        for field, other_field in fields:

            providers = data.get(field, [])

            if providers:
                if not isinstance(providers, list):
                    raise serializers.ValidationError({
                        field: ["Must be a list"]
                    })

                invalid = [
                    p for p in providers
                    if p not in PROVIDER_CHOICES
                ]

                if invalid:
                    raise serializers.ValidationError({
                        field: [
                            f"Invalid provider(s): {invalid}. "
                            f"Allowed: {PROVIDER_CHOICES}"
                        ]
                    })

            # If Others selected → require free text
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
            "airfiber",           # ✅ Added
            "others_airfiber",    # ✅ Added
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

class FullSubSiteSerializer(serializers.ModelSerializer):

    location_details = SurveyLocationSerializer(source="surveylocation", read_only=True)
    monument = SurveyMonumentSerializer(source="surveymonument", read_only=True)
    sky_visibility = SurveySkyVisibilitySerializer(source="surveyskyvisibility", read_only=True)
    power = SurveyPowerSerializer(source="surveypower", read_only=True)
    connectivity = SurveyConnectivitySerializer(source="surveyconnectivity", read_only=True)
    photos = SurveyPhotoSerializer(read_only=True)

    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "location",
            "priority",
            "created_at",
            "location_details",
            "monument",
            "sky_visibility",
            "power",
            "connectivity",
            "photos",
        ]
class FullHierarchySurveySerializer(serializers.ModelSerializer):

    state = serializers.CharField(source="state.name", read_only=True)
    district = serializers.CharField(source="district.name", read_only=True)
    subdistrict = serializers.CharField(source="subdistrict.name", read_only=True)
    station = serializers.CharField(source="station.name", read_only=True)

    subsites = FullSubSiteSerializer(many=True, read_only=True)
    surveyor_name = serializers.CharField(source="surveyor.name", read_only=True)
    surveyor_username = serializers.CharField(source="surveyor.username", read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "state",
            "district",
            "subdistrict",
            "station",
            "status",
            "remarks",
            "created_at",
            "surveyor_name",
            "surveyor_username",
            "subsites",
        ]

# class FullHierarchySurveySerializer(serializers.ModelSerializer):

#     subsites = FullSubSiteSerializer(many=True, read_only=True)
#     surveyor_name = serializers.CharField(source="surveyor.name", read_only=True)
#     surveyor_username = serializers.CharField(source="surveyor.username", read_only=True)

#     class Meta:
#         model = Survey
#         fields = [
#             "id",
#             "state",
#             "district",
#             "subdistrict",
#             "station",
#             "status",
#             "remarks",
#             "created_at",
#             "surveyor_name",
#             "surveyor_username",
#             "subsites",
#         ]
        
        

class TownSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Town
        fields = ["id", "name"]

    def get_name(self, obj):
        if obj.sequence > 1:
            return f"{obj.base_name} {obj.sequence}"
        return obj.base_name


class SubDistrictSerializer(serializers.ModelSerializer):
    towns = TownSerializer(many=True)

    class Meta:
        model = SubDistrict
        fields = ["id", "name", "towns"]


class DistrictSerializer(serializers.ModelSerializer):
    subdistricts = SubDistrictSerializer(many=True)

    class Meta:
        model = District
        fields = ["id", "name", "subdistricts"]


class StateSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True)

    class Meta:
        model = State
        fields = ["id", "name", "latitude", "longitude", "districts"]






class DistrictdbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Districtdb
        fields = [
            "id",
            "state",
            "name",
            "latitude",
            "longitude",
        ]
        


class StationdbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stationdb
        fields = [
            "id",
            "district",
            "sl_no",
            "name",
            "code",
            "latitude",
            "longitude",
            "height",
        ]
        
        
        

class SupervisorSubsiteSerializer(serializers.ModelSerializer):

    location_details = SurveyLocationSerializer(source="surveylocation", read_only=True)
    monument_details = SurveyMonumentSerializer(source="surveymonument", read_only=True)
    sky_visibility = SurveySkyVisibilitySerializer(source="surveyskyvisibility", read_only=True)
    power_details = SurveyPowerSerializer(source="surveypower", read_only=True)
    connectivity_details = SurveyConnectivitySerializer(source="surveyconnectivity", read_only=True)
    photo_details = SurveyPhotoSerializer(source="photos", read_only=True)

    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "location",
            "priority",
            "status",
            "rinex_file",
            "contact_details",
            "location_details",
            "monument_details",
            "sky_visibility",
            "power_details",
            "connectivity_details",
            "photo_details",
            "created_at"
        ]
        
class SupervisorSurveySerializer(serializers.ModelSerializer):

    site_name = serializers.CharField(source="station.name", read_only=True)
    latitude=serializers.CharField(source="station.latitude", read_only=True)
    longitude=serializers.CharField(source="station.longitude", read_only=True)
    surveyor_name = serializers.CharField(source="surveyor.username", read_only=True)

    subsites = SupervisorSubsiteSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "site_name",
            "latitude",
            "longitude",
            "status",
            "surveyor_name",
            "remarks",
            "created_at",
            "subsites"
        ]

class DirectorSubsiteSerializer(serializers.ModelSerializer):

    site_name = serializers.CharField(source="survey.station.name", read_only=True)
    latitude=serializers.CharField(source="survey.station.latitude", read_only=True)
    longitude=serializers.CharField(source="survey.station.longitude", read_only=True)
    surveyor_name = serializers.CharField(source="survey.surveyor.username", read_only=True)

    supervisor_name = serializers.SerializerMethodField()

    location_details = SurveyLocationSerializer(
        source="surveylocation",
        read_only=True
    )

    monument_details = SurveyMonumentSerializer(
        source="surveymonument",
        read_only=True
    )

    sky_visibility = SurveySkyVisibilitySerializer(
        source="surveyskyvisibility",
        read_only=True
    )

    power_details = SurveyPowerSerializer(
        source="surveypower",
        read_only=True
    )

    connectivity_details = SurveyConnectivitySerializer(
        source="surveyconnectivity",
        read_only=True
    )

    photo_details = SurveyPhotoSerializer(
    source="photos",
    read_only=True
    )

    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "site_name",
            "latitude",
            "longitude",
            "location",
            "priority",
            "status",
            "rinex_file",
            "contact_details",
            "surveyor_name",
            "supervisor_name",
            "location_details",
            "monument_details",
            "sky_visibility",
            "power_details",
            "connectivity_details",
            "photo_details",
            "created_at"
        ]

    def get_supervisor_name(self, obj):

        approval = SurveyApproval.objects.filter(
            survey=obj.survey,
            approval_level=1
        ).select_related("approved_by").first()

        if approval:
            return approval.approved_by.username

        return None
    
    
class ZonalSubsiteSerializer(serializers.ModelSerializer):

    site_name = serializers.CharField(source="survey.station.name", read_only=True)
    latitude=serializers.CharField(source="survey.station.latitude", read_only=True)
    longitude=serializers.CharField(source="survey.station.longitude", read_only=True)
    surveyor_name = serializers.CharField(source="survey.surveyor.username", read_only=True)

    supervisor_name = serializers.SerializerMethodField()
    director_name = serializers.SerializerMethodField()

    location_details = SurveyLocationSerializer(
        source="surveylocation",
        read_only=True
    )

    monument_details = SurveyMonumentSerializer(
        source="surveymonument",
        read_only=True
    )

    sky_visibility = SurveySkyVisibilitySerializer(
        source="surveyskyvisibility",
        read_only=True
    )

    power_details = SurveyPowerSerializer(
        source="surveypower",
        read_only=True
    )

    connectivity_details = SurveyConnectivitySerializer(
        source="surveyconnectivity",
        read_only=True
    )

    photo_details = SurveyPhotoSerializer(
    source="photos",
    read_only=True
    )

    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "site_name",
            "latitude",
            "longitude",
            "location",
            "priority",
            "status",
            "rinex_file",
            "contact_details",
            "surveyor_name",
            "supervisor_name",
            "director_name",
            "location_details",
            "monument_details",
            "sky_visibility",
            "power_details",
            "connectivity_details",
            "photo_details",
            "created_at"
        ]

    def get_supervisor_name(self, obj):

        approval = SurveyApproval.objects.filter(
            survey=obj.survey,
            approval_level=1
        ).select_related("approved_by").first()

        if approval:
            return approval.approved_by.username

        return None


    def get_director_name(self, obj):

        approval = SurveyApproval.objects.filter(
            subsite=obj,
            approval_level=2
        ).select_related("approved_by").first()

        if approval:
            return approval.approved_by.username

        return None
    
    
class GNRBSubsiteSerializer(serializers.ModelSerializer):

    site_name = serializers.CharField(source="survey.station.name", read_only=True)
    latitude=serializers.CharField(source="survey.station.latitude", read_only=True)
    longitude=serializers.CharField(source="survey.station.longitude", read_only=True)
    surveyor_name = serializers.CharField(source="survey.surveyor.username", read_only=True)

    supervisor_name = serializers.SerializerMethodField()
    director_name = serializers.SerializerMethodField()
    zonal_chief_name = serializers.SerializerMethodField()

    location_details = SurveyLocationSerializer(
        source="surveylocation",
        read_only=True
    )

    monument_details = SurveyMonumentSerializer(
        source="surveymonument",
        read_only=True
    )

    sky_visibility = SurveySkyVisibilitySerializer(
        source="surveyskyvisibility",
        read_only=True
    )

    power_details = SurveyPowerSerializer(
        source="surveypower",
        read_only=True
    )

    connectivity_details = SurveyConnectivitySerializer(
        source="surveyconnectivity",
        read_only=True
    )

    photo_details = SurveyPhotoSerializer(
    source="photos",
    read_only=True
    )

    class Meta:
        model = SurveySubSite
        fields = [
            "id",
            "site_name",
            "latitude",
            "longitude",
            "location",
            "priority",
            "status",
            "rinex_file",
            "contact_details",
            "surveyor_name",
            "supervisor_name",
            "director_name",
            "zonal_chief_name",
            "location_details",
            "monument_details",
            "sky_visibility",
            "power_details",
            "connectivity_details",
            "photo_details",
            "created_at"
        ]


    def get_supervisor_name(self, obj):

        approval = SurveyApproval.objects.filter(
            survey=obj.survey,
            approval_level=1
        ).select_related("approved_by").first()

        if approval:
            return approval.approved_by.username

        return None


    def get_director_name(self, obj):

        approval = SurveyApproval.objects.filter(
            subsite=obj,
            approval_level=2
        ).select_related("approved_by").first()

        if approval:
            return approval.approved_by.username

        return None


    def get_zonal_chief_name(self, obj):

        approval = SurveyApproval.objects.filter(
            subsite=obj,
            approval_level=3
        ).select_related("approved_by").first()

        if approval:
            return approval.approved_by.username

        return None