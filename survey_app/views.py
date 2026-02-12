from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated 
from rest_framework import status 
from django.db import transaction
from .models import *
from .serializers import *
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser



class SignupAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = Token.objects.get(user=user)

        return Response({
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "token": token.key
        })

class LoginAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "token": token.key
        })

class AllUsersAPI(APIView):
    permission_classes = [IsAuthenticated]  # Change if needed

    def get(self, request):
        users = User.objects.all().order_by("-created_at")
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoleWiseUsersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, role):

        # Validate role
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]

        if role.upper() not in valid_roles:
            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        users = User.objects.filter(role=role.upper())

        serializer = UserListSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



def home(request):
    return render(request, "home.html")

ROLE_FLOW = {
    "SUPERVISOR": ("SUBMITTED", "SUPERVISOR_APPROVED", 1),
    "DIRECTOR": ("SUPERVISOR_APPROVED", "DIRECTOR_APPROVED", 2),
    "ZONAL_CHIEF": ("DIRECTOR_APPROVED", "ZONAL_CHIEF_APPROVED", 3),
    "GNRB": ("ZONAL_CHIEF_APPROVED", "GNRB_APPROVED", 4),
}


#Create Survey (MULTIPLE SITES)
class SurveyCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(surveyor=request.user)
            return Response(serializer.data)
            # return Response({"message": "Survey created successfully", "survey_id": serializer.data['id']}, status=201)
        else:
            return Response(serializer.errors, status=400)
    
    # def post(self, request):
    # # 🔍 only site_name duplicate check
    #     if Survey.objects.filter(site_name=request.data.get("site_name")).exists():
    #         return Response(
    #             {"site_name": "Survey with this site name already exists"},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     serializer = SurveySerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(surveyor=request.user)

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    def get(self, request, survey_id=None):
        if survey_id:
            survey = get_object_or_404(Survey, id=survey_id, surveyor=request.user)
            serializer = SurveySerializer(survey)
        else:
            surveys = Survey.objects.filter(surveyor=request.user)
            serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)

    def delete(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, surveyor=request.user)
        survey.delete()
        return Response({"message": "Survey deleted successfully"}, status=204)
    def put(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id, surveyor=request.user)
        serializer = SurveySerializer(survey, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

class SurveyFullDataAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id)

        data = {
            "survey_id": str(survey.id),
            "site_name": survey.site_name,
            "status": survey.status,
            "subsites": []
        }

        for subsite in survey.subsites.all():

            # Handle ONE photo safely
            photo_obj = getattr(subsite, "photos", None)
            photo_data = (
                SurveyPhotoSerializer(photo_obj).data
                if photo_obj else None
            )

            subsite_data = {
                "subsite_id": str(subsite.id),
                "subsite_name": subsite.subsite_name,

                "location": SurveyLocationSerializer(
                    getattr(subsite, "surveylocation", None)
                ).data if hasattr(subsite, "surveylocation") else None,

                "monument": SurveyMonumentSerializer(
                    getattr(subsite, "surveymonument", None)
                ).data if hasattr(subsite, "surveymonument") else None,

                "sky_visibility": SurveySkyVisibilitySerializer(
                    getattr(subsite, "surveyskyvisibility", None)
                ).data if hasattr(subsite, "surveyskyvisibility") else None,

                "power": SurveyPowerSerializer(
                    getattr(subsite, "surveypower", None)
                ).data if hasattr(subsite, "surveypower") else None,

                "connectivity": SurveyConnectivitySerializer(
                    getattr(subsite, "surveyconnectivity", None)
                ).data if hasattr(subsite, "surveyconnectivity") else None,

                # SINGLE photo (OneToOne)
                "photo": photo_data
            }

            data["subsites"].append(subsite_data)

        return Response(data)


class SurveyListByUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        surveys = Survey.objects.filter(surveyor=request.user).order_by("-created_at")
        serializer = SurveySerializer(surveys, many=True)

        return Response({
            "count": surveys.count(),
            "surveys": serializer.data
        })


class SurveySubmitAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, survey_id):

        survey = get_object_or_404(
            Survey,
            id=survey_id,
            surveyor=request.user
        )

        # ✅ Allow only DRAFT or REJECTED
        if survey.status not in ["DRAFT", "REJECTED"]:
            return Response(
                {
                    "error": f"Survey cannot be submitted in current state ({survey.status})"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        subsites = survey.subsites.all()

        if not subsites.exists():
            return Response(
                {"error": "No subsites found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        incomplete_subsites = []

        for subsite in subsites:
            missing = []

            if not hasattr(subsite, "surveylocation"):
                missing.append("Location")

            if not hasattr(subsite, "surveymonument"):
                missing.append("Monument")

            if not hasattr(subsite, "surveyskyvisibility"):
                missing.append("Sky Visibility")

            if not hasattr(subsite, "surveypower"):
                missing.append("Power")

            if not hasattr(subsite, "surveyconnectivity"):
                missing.append("Connectivity")

            # ✅ Photos check (OneToOne safe)
            try:
                photos = subsite.photos
            except SurveyPhoto.DoesNotExist:
                photos = None

            if not photos:
                missing.append("Photos")
            else:
                if not all([
                    photos.north_photo,
                    photos.east_photo,
                    photos.south_photo,
                    photos.west_photo
                ]):
                    missing.append("All 4 directional photos required")

            if missing:
                incomplete_subsites.append({
                    "subsite_id": str(subsite.id),
                    "subsite_name": subsite.subsite_name,
                    "missing": missing
                })

        # ❌ Validation failed
        if incomplete_subsites:
            return Response(
                {
                    "error": "Survey cannot be submitted",
                    "current_status": survey.status,
                    "incomplete_subsites": incomplete_subsites
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ SUBMIT / RE-SUBMIT
        survey.status = "SUBMITTED"

        # clear rejection reason if exists
        if hasattr(survey, "rejection_reason"):
            survey.rejection_reason = None

        survey.save(update_fields=["status"])

        return Response(
            {
                "message": "Survey submitted successfully",
                "survey_id": survey.id,
                "status": survey.status
            },
            status=status.HTTP_200_OK
        )


class SurveySubSiteCreateAPI(APIView):
    permission_classes = [IsAuthenticated]
    # CREATE SUBSITE
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id)

        serializer = SurveySubSiteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subsite = serializer.save(survey=survey)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    "errors": serializer.errors,
                    "priority": 1   # 👈 default priority explicitly show
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # LIST SUBSITES
    def get(self, request, survey_id,  subsite_id=None):
            # 🔹 Get single subsite
        if subsite_id:
            subsite = get_object_or_404(SurveySubSite,id=subsite_id,survey_id=survey_id)
            serializer = SurveySubSiteSerializer(subsite)
            return Response(serializer.data)

        # 🔹 Get all subsites of a survey
        subsites = SurveySubSite.objects.filter(survey_id=survey_id)
        serializer = SurveySubSiteSerializer(subsites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # UPDATE SUBSITE
    def put(self, request, survey_id, subsite_id):
        subsite = get_object_or_404(
            SurveySubSite,
            id=subsite_id,
            survey_id=survey_id
        )

        serializer = SurveySubSiteSerializer(
            subsite,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE SUBSITE
    def delete(self, request, survey_id, subsite_id):
        subsite = get_object_or_404(
            SurveySubSite,
            id=subsite_id,
            survey_id=survey_id
        )
        subsite.delete()

        return Response(
            {"message": "Subsite deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
#Survey Location       
class SurveyLocationAPI(APIView):
    permission_classes = [IsAuthenticated]
    # def post(self, request, subsite_id=None):
    #     serializer = SurveyLocationSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         subsite = get_object_or_404(SurveySubSite, id=subsite_id)
    #         serializer.save(survey=subsite)
    #         # return Response(serializer.data, status=201)
    #         return Response({"message": "Location created successfully", "location_id": serializer.data['id']}, status=201)
    #     else:
    #         return Response(serializer.errors, status=400)
    def post(self, request, subsite_id=None):

        subsite = get_object_or_404(SurveySubSite, id=subsite_id)

        # ✅ CHECK: Location already exists
        if hasattr(subsite, "surveylocation"):
            return Response(
                {
                    "message": "Location data already exists for this subsite",
                    "location_id": subsite.surveylocation.id
                },
                status=status.HTTP_200_OK
            )

        serializer = SurveyLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(survey=subsite)

        return Response(serializer.data, status=201)

    def get(self, request, subsite_id=None):
        locations = SurveyLocation.objects.filter(survey_id=subsite_id)
        serializer = SurveyLocationSerializer(locations, many=True)
        return Response(serializer.data)
    def put(self, request, subsite_id=None):
        location = get_object_or_404(SurveyLocation, survey_id=subsite_id)
        serializer = SurveyLocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
    def delete(self, request, subsite_id=None):
        location = get_object_or_404(SurveyLocation, survey_id=subsite_id)
        location.delete()
        return Response({"message": "Location deleted successfully"}, status=204)


#Survey Monument
class SurveyMonumentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, subsite_id=None):

        subsite = get_object_or_404(SurveySubSite, id=subsite_id)

        # ✅ CHECK: Monument already exists
        if hasattr(subsite, "surveymonument"):
            return Response(
                {
                    "message": "Monument data already exists for this subsite",
                    "monument_id": subsite.surveymonument.id
                },
                status=status.HTTP_200_OK
            )

        serializer = SurveyMonumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(survey=subsite)

        return Response(
            {
                "message": "Monument created successfully",
                "monument_id": serializer.data["id"]
            },
            status=status.HTTP_201_CREATED
        )
    def get(self, request, subsite_id=None):
        monuments = SurveyMonument.objects.filter(survey_id=subsite_id)
        serializer = SurveyMonumentSerializer(monuments, many=True)
        return Response(serializer.data)
    def put(self, request, subsite_id=None):
        monument = get_object_or_404(SurveyMonument, survey_id=subsite_id)
        serializer = SurveyMonumentSerializer(monument, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
    def delete(self, request, subsite_id=None):
        monument = get_object_or_404(SurveyMonument, survey_id=subsite_id)
        monument.delete()
        return Response({"message": "Monument deleted successfully"}, status=204)

#Survey Sky Visibility
class SurveySkyVisibilityAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # CREATE
    def post(self, request, subsite_id):
        subsite = get_object_or_404(SurveySubSite, id=subsite_id)

        if hasattr(subsite, "surveyskyvisibility"):
            return Response(
                {"error": "Sky Visibility already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SurveySkyVisibilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sky = serializer.save(survey=subsite)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

    # READ
    def get(self, request, subsite_id):
        sky = get_object_or_404(
            SurveySkyVisibility,
            survey_id=subsite_id
        )
        serializer = SurveySkyVisibilitySerializer(sky)
        return Response(serializer.data)

    # UPDATE
    def put(self, request, subsite_id):
        sky = get_object_or_404(
            SurveySkyVisibility,
            survey_id=subsite_id
        )

        serializer = SurveySkyVisibilitySerializer(
            sky,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # DELETE
    def delete(self, request, subsite_id):
        sky = get_object_or_404(
            SurveySkyVisibility,
            survey_id=subsite_id
        )
        sky.delete()

        return Response(
            {"message": "Deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
#ADD POWER DETAILS
class SurveyPowerAPI(APIView):
    permission_classes = [IsAuthenticated]
    # def post(self, request, subsite_id=None):
    #     serializer = SurveyPowerSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.is_valid(raise_exception=True)
    #         subsite = get_object_or_404(SurveySubSite, id=subsite_id)
    #         serializer.save(survey=subsite)
    #         return Response({"message": "Power Details created successfully", "power_id": serializer.data['id']}, status=201)
    #     else:
    #         return Response(serializer.errors, status=400)
    def post(self, request, subsite_id=None):

        subsite = get_object_or_404(SurveySubSite, id=subsite_id)

        # ✅ CHECK: Power details already exist
        if hasattr(subsite, "surveypower"):
            return Response(
                {
                    "message": "Power details already exist for this subsite",
                    "power_id": subsite.surveypower.id
                },
                status=status.HTTP_200_OK
            )

        serializer = SurveyPowerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(survey=subsite)

        return Response(
            {
                "message": "Power details created successfully",
                "power_id": serializer.data["id"]
            },
            status=status.HTTP_201_CREATED
        )
    def get(self, request, subsite_id=None):
        powers = SurveyPower.objects.filter(survey_id=subsite_id)
        serializer = SurveyPowerSerializer(powers, many=True)
        return Response(serializer.data)
    def put(self, request, subsite_id=None):
        power = get_object_or_404(SurveyPower, survey_id=subsite_id)
        serializer = SurveyPowerSerializer(power, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
    def delete(self, request, subsite_id=None):
        power = get_object_or_404(SurveyPower, survey_id=subsite_id)
        power.delete()
        return Response({"message": "Power Details deleted successfully"}, status=204)

#ADD CONNECTIVITY
class SurveyConnectivityAPI(APIView):
    permission_classes = [IsAuthenticated]

    # CREATE
    def post(self, request, subsite_id=None):
        subsite = get_object_or_404(SurveySubSite, id=subsite_id)

        if hasattr(subsite, "surveyconnectivity"):
            return Response(
                {
                    "message": "Connectivity details already exist",
                    "connectivity_id": subsite.surveyconnectivity.id
                },
                status=status.HTTP_200_OK
            )
    
        serializer = SurveyConnectivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        connectivity = serializer.save(survey=subsite)

        return Response(
            {
                "message": "Connectivity details created successfully",
                "connectivity_id": connectivity.id
            },
            status=status.HTTP_201_CREATED
        )

    # GET
    def get(self, request, subsite_id=None):
        connectivity = get_object_or_404(
            SurveyConnectivity,
            survey_id=subsite_id
        )
        serializer = SurveyConnectivitySerializer(connectivity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # UPDATE
    def put(self, request, subsite_id=None):
        connectivity = get_object_or_404(
            SurveyConnectivity,
            survey_id=subsite_id
        )

        serializer = SurveyConnectivitySerializer(
            connectivity,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE
    def delete(self, request, subsite_id=None):
        connectivity = get_object_or_404(
            SurveyConnectivity,
            survey_id=subsite_id
        )
        connectivity.delete()

        return Response(
            {"message": "Connectivity details deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )   
#UPLOAD PHOTOS
class SurveyPhotoUploadAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, subsite_id=None):

        subsite = get_object_or_404(SurveySubSite, id=subsite_id)

        # ✅ CHECK: Photos already exist
        try:
            photos = subsite.photos   # related_name="photos"
        except SurveyPhoto.DoesNotExist:
            photos = None

        if photos:
            return Response(
                {
                    "message": "Photo data already exists for this subsite",
                    "photo_id": photos.id
                },
                status=status.HTTP_200_OK
            )

        serializer = SurveyPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sub_site=subsite)

        return Response(
            {
                "message": "Photos uploaded successfully",
                "photo_id": serializer.data["id"]
            },
            status=status.HTTP_201_CREATED
        )
    def get(self, request, subsite_id=None):
        subsite = get_object_or_404(SurveySubSite, id=subsite_id)
        photos = SurveyPhoto.objects.filter(sub_site=subsite)
        serializer = SurveyPhotoSerializer(photos, many=True)
        return Response(serializer.data)
    def delete(self, request, subsite_id=None, photo_id=None):
        photo = get_object_or_404(SurveyPhoto, id=photo_id, sub_site_id=subsite_id)
        photo.delete()
        return Response({"message": "Photo deleted successfully"}, status=204)
    
    def put(self, request, subsite_id=None, photo_id=None):
        photo = get_object_or_404(SurveyPhoto, id=photo_id, sub_site_id=subsite_id)
        serializer = SurveyPhotoSerializer(photo, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
        

class SurveyApprovalAPI(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, survey_id):
        user = request.user
        decision = request.data.get("decision")
        remarks = request.data.get("remarks", "")

        if decision not in ["APPROVED", "REJECTED"]:
            return Response(
                {"error": "Decision must be APPROVED or REJECTED"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role not in ROLE_FLOW:
            return Response(
                {"error": "You are not allowed to approve"},
                status=status.HTTP_403_FORBIDDEN
            )

        required_status, next_status, level = ROLE_FLOW[user.role]

        survey = get_object_or_404(Survey, id=survey_id)

        # 🚫 Prevent self approval
        if survey.surveyor == user:
            return Response(
                {"error": "You cannot approve your own survey"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ❌ Wrong status order
        if survey.status != required_status:
            return Response(
                {"error": f"Survey must be in {required_status} state"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ❌ Already approved
        if SurveyApproval.objects.filter(
            survey=survey,
            approval_level=level,
            decision="APPROVED"
        ).exists():
            return Response(
                {"error": "Already approved at this level"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Save approval record
        SurveyApproval.objects.create(
            survey=survey,
            approval_level=level,
            approved_by=user,
            decision=decision,
            remarks=remarks
        )

        # ✅ Update status
        survey.status = next_status if decision == "APPROVED" else "REJECTED"
        survey.save(update_fields=["status"])

        return Response(
            {
                "message": "Decision recorded successfully",
                "new_status": survey.status
            },
            status=status.HTTP_200_OK
        )

     
#Pending Survey List      
class PendingSurveyAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Surveyor → apni surveys
        if user.role == "SURVEYOR":
            surveys = Survey.objects.filter(surveyor=user)

        # Approver roles → status based
        elif user.role in ROLE_FLOW:
            required_status = ROLE_FLOW[user.role][0]
            surveys = Survey.objects.filter(status=required_status)

        else:
            surveys = Survey.objects.none()

        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)




from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from survey_app.forms import UserSignupForm, UserLoginForm


# -------------------------
# SIGNUP VIEW
# -------------------------
def signup_view(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # auto login after signup
            return redirect("survey-map")
    else:
        form = UserSignupForm()

    return render(request, "signup.html", {"form": form})


# -------------------------
# LOGIN VIEW
# -------------------------
def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("survey-map")
    else:
        form = UserLoginForm()

    return render(request, "login.html", {"form": form})


# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    logout(request)
    return redirect("login")


def survey_map_view(request):
    return render(request, "map.html")


class SurveyMapDataAPI(APIView):

    def get(self, request):
        data = []

        locations = SurveyLocation.objects.select_related("survey")

        for loc in locations:
            try:
                photos = loc.survey.photos
            except SurveyPhoto.DoesNotExist:
                photos = None

            data.append({
                "id": str(loc.survey.id),
                "lat": float(loc.latitude),
                "lon": float(loc.longitude),
                "address": loc.address,
                "city": loc.city,
                "district": loc.district,
                "state": loc.state,
                "photos": {
                    "north": photos.north_photo.url if photos and photos.north_photo else None,
                    "east": photos.east_photo.url if photos and photos.east_photo else None,
                    "south": photos.south_photo.url if photos and photos.south_photo else None,
                    "west": photos.west_photo.url if photos and photos.west_photo else None,
                }
            })

        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = SurveyLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subsite = serializer.validated_data["survey"]

        # ✅ Prevent duplicate
        if hasattr(subsite, "surveylocation"):
            return Response(
                {
                    "message": "Location data already exists",
                    "location_id": subsite.surveylocation.id
                },
                status=status.HTTP_200_OK
            )

        location = serializer.save()

        return Response(
            {
                "message": "Location created successfully",
                "location_id": location.id
            },
            status=status.HTTP_201_CREATED
        )
    def put(self, request, location_id):
        location = get_object_or_404(SurveyLocation, id=location_id)

        serializer = SurveyLocationSerializer(
            location,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Location updated successfully",
                "location_id": location.id
            },
            status=status.HTTP_200_OK
        )
        
    def delete(self, request, location_id):
        location = get_object_or_404(SurveyLocation, id=location_id)
        location.delete()

        return Response(
            {"message": "Location deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )





class RinexUploadAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # ✅ CREATE
    def post(self, request):

        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES["file"]

        # Duplicate check (same user + same filename)
        if RinexFile.objects.filter(
            uploaded_by=request.user,
            file__endswith=uploaded_file.name
        ).exists():
            return Response(
                {"message": "This file already exists"},
                status=status.HTTP_200_OK
            )

        serializer = RinexFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rinex = serializer.save(uploaded_by=request.user)

        return Response(
            {
                "message": "RINEX file uploaded successfully",
                "rinex_id": rinex.id
            },
            status=status.HTTP_201_CREATED
        )

    # ✅ GET (ALL or SINGLE)
    def get(self, request, file_id=None):

        if file_id:
            rinex = get_object_or_404(
                RinexFile,
                id=file_id,
                uploaded_by=request.user
            )
            serializer = RinexFileSerializer(rinex)
            return Response(serializer.data)

        files = RinexFile.objects.filter(uploaded_by=request.user)
        serializer = RinexFileSerializer(files, many=True)
        return Response(serializer.data)

    # ✅ UPDATE (Replace file)
    def put(self, request, file_id):

        rinex = get_object_or_404(
            RinexFile,
            id=file_id,
            uploaded_by=request.user
        )

        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete old file from storage
        if rinex.file:
            rinex.file.delete()

        serializer = RinexFileSerializer(
            rinex,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "RINEX file updated successfully",
                "rinex_id": rinex.id
            },
            status=status.HTTP_200_OK
        )

    # ✅ DELETE
    def delete(self, request, file_id):

        rinex = get_object_or_404(
            RinexFile,
            id=file_id,
            uploaded_by=request.user
        )

        # Delete physical file
        if rinex.file:
            rinex.file.delete()

        rinex.delete()

        return Response(
            {"message": "RINEX file deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )




# 🔹 Role Flow Mapping
from django.db.models import Prefetch
ROLE_FLOW = {
    "SUPERVISOR": "SURVEYOR",
    "DIRECTOR": "SUPERVISOR",
    "ZONAL_CHIEF": "DIRECTOR",
    "GNRB": "ZONAL_CHIEF",
}


class HierarchySiteSubSiteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        current_user = request.user
        current_role = current_user.role

        # ❌ Surveyor & Admin not allowed
        if current_role not in ROLE_FLOW:
            return Response(
                {"error": "You are not allowed to view this data"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 🔹 Find target role
        target_role = ROLE_FLOW[current_role]

        # 🔹 Get lower level users (same zone)
        lower_users = User.objects.filter(
            role=target_role,
            zone=current_user.zone
        )

        # 🔹 Get their surveys with subsites
        surveys = Survey.objects.filter(
            surveyor__in=lower_users
        ).prefetch_related(
            Prefetch("subsites")
        ).order_by("-created_at")

        serializer = SiteWithSubSiteSerializer(surveys, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)