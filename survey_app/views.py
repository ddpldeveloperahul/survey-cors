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
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP
from rest_framework.authentication import TokenAuthentication



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



class LogoutAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's token
        request.user.auth_token.delete()

        return Response({
            "message": "Logout successful"
        })

class ForgotPasswordAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Delete old OTP
        PasswordResetOTP.objects.filter(user=user).delete()

        # Save new OTP
        PasswordResetOTP.objects.create(user=user, otp=otp)

        # Send Email
        send_mail(
            subject="Your Password Reset OTP",
            message=f"Hello {user.username},\n\nYour OTP is: {otp}\n\nValid for 10 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to your email"})
    
class ResetPasswordAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.get(user=user, otp=otp)
        except:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp_obj.is_expired():
            otp_obj.delete()
            return Response({"error": "OTP expired"}, status=400)

        # ✅ Set new password
        user.set_password(new_password)
        user.save()

        otp_obj.delete()

        return Response({"message": "Password reset successful"})
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
            "site_name": survey.station.name,  # ✅ FIXED
            "status": survey.status,
            "subsites": []
        }

        for subsite in survey.subsites.all():

            photo_obj = getattr(subsite, "photos", None)
            photo_data = (
                SurveyPhotoSerializer(photo_obj).data
                if photo_obj else None
            )

            subsite_data = {
                "subsite_id": str(subsite.id),
                "subsite_name": subsite.location,
                "priority": subsite.priority,
                "rinex_file": subsite.rinex_file.url if subsite.rinex_file else None,

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

                "photo": photo_data
            }

            data["subsites"].append(subsite_data)

        return Response(data)

class SurveyListByUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     surveys = Survey.objects.filter(surveyor=request.user).order_by("-created_at")
    #     serializer = SurveySerializer(surveys, many=True)

    #     return Response({
    #         "count": surveys.count(),
    #         "surveys": serializer.data
    #     })
    def get(self, request):
        surveys = Survey.objects.filter(
            surveyor=request.user
        ).select_related(
            "state", "district", "subdistrict", "station"
        ).order_by("-created_at")

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
                    "subsite_name": subsite.location,
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
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # CREATE
    def post(self, request, survey_id):

        survey = get_object_or_404(Survey, id=survey_id)

        serializer = SurveySubSiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subsite = serializer.save(survey=survey)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )



    # GET
    def get(self, request, survey_id, subsite_id=None):

        if subsite_id:
            subsite = get_object_or_404(
                SurveySubSite,
                id=subsite_id,
                survey_id=survey_id
            )
            serializer = SurveySubSiteSerializer(subsite)
            return Response(serializer.data)

        subsites = SurveySubSite.objects.filter(survey_id=survey_id)
        serializer = SurveySubSiteSerializer(subsites, many=True)
        return Response(serializer.data)

    # UPDATE
    # def put(self, request, survey_id, subsite_id):

    #     subsite = get_object_or_404(
    #         SurveySubSite,
    #         id=subsite_id,
    #         survey_id=survey_id
    #     )

    #     serializer = SurveySubSiteSerializer(
    #         subsite,
    #         data=request.data,
    #         partial=True
    #     )

    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     return Response(serializer.data)
    def put(self, request, survey_id, subsite_id):

        subsite = get_object_or_404(
            SurveySubSite,
            id=subsite_id,
            survey_id=survey_id
        )

        # ❌ Prevent update after submission
        if subsite.survey.status == "SUBMITTED":
            return Response(
                {"error": "Cannot edit subsite after survey submission"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SurveySubSiteSerializer(
            subsite,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # DELETE
    # def delete(self, request, survey_id, subsite_id):

    #     subsite = get_object_or_404(
    #         SurveySubSite,
    #         id=subsite_id,
    #         survey_id=survey_id
    #     )

    #     subsite.delete()

    #     return Response(
    #         {"message": "Subsite deleted successfully"},
    #         status=status.HTTP_204_NO_CONTENT
    #     )    

    def delete(self, request, survey_id, subsite_id):

        subsite = get_object_or_404(
            SurveySubSite,
            id=subsite_id,
            survey_id=survey_id
        )

        # ❌ Prevent delete after submission
        if subsite.survey.status == "SUBMITTED":
            return Response(
                {"error": "Cannot delete subsite after survey submission"},
                status=status.HTTP_400_BAD_REQUEST
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

class SurveySkyVisibilityAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser,JSONParser]

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


class SurveyPowerAPI(APIView):

    permission_classes = [IsAuthenticated]

    # CREATE
    def post(self, request, subsite_id):

        subsite = get_object_or_404(SurveySubSite, id=subsite_id)

        if hasattr(subsite, "surveypower"):
            return Response(
                {
                    "message": "Power details already exist",
                    "power_id": subsite.surveypower.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SurveyPowerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        power = serializer.save(survey=subsite)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    # READ
    def get(self, request, subsite_id):

        power = get_object_or_404(
            SurveyPower,
            survey_id=subsite_id
        )

        serializer = SurveyPowerSerializer(power)
        return Response(serializer.data)

    # UPDATE
    def put(self, request, subsite_id):

        power = get_object_or_404(
            SurveyPower,
            survey_id=subsite_id
        )

        serializer = SurveyPowerSerializer(
            power,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # DELETE
    def delete(self, request, subsite_id):

        power = get_object_or_404(
            SurveyPower,
            survey_id=subsite_id
        )

        power.delete()

        return Response(
            {"message": "Power Details deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

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
            # {
            #     "message": "Connectivity details created successfully",
            #     "connectivity_id": connectivity.id
            # },
            serializer.data,
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


class HierarchySurveyAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user
        role = user.role
        zone = user.zone

        # 🔹 SURVEYOR → Only his own data
        if role == "SURVEYOR":
            surveys = Survey.objects.filter(
                surveyor=user
            )

        # 🔹 SUPERVISOR → Surveyor SUBMITTED data
        elif role == "SUPERVISOR":
            surveys = Survey.objects.filter(
                surveyor__zone=zone,
                status="SUBMITTED"
            )

        # 🔹 DIRECTOR → Supervisor Approved data
        elif role == "DIRECTOR":
            surveys = Survey.objects.filter(
                surveyor__zone=zone,
                status="SUPERVISOR_APPROVED"
            )

        # 🔹 ZONAL CHIEF → Director Approved data
        elif role == "ZONAL_CHIEF":
            surveys = Survey.objects.filter(
                surveyor__zone=zone,
                status="DIRECTOR_APPROVED"
            )

        # 🔹 GNRB → Zonal Chief Approved data
        elif role == "GNRB":
            surveys = Survey.objects.filter(
                surveyor__zone=zone,
                status="ZONAL_CHIEF_APPROVED"
            )

        else:
            return Response(
                {"error": "You are not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )

        surveys = surveys.select_related("surveyor").prefetch_related(
            "subsites__surveylocation",
            "subsites__surveymonument",
            "subsites__surveyskyvisibility",
            "subsites__surveypower",
            "subsites__surveyconnectivity",
            "subsites__photos",
        ).order_by("-created_at")

        serializer = FullHierarchySurveySerializer(surveys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class StateListAPI(APIView):
    def get(self, request, state_id=None):

        # 🔹 If specific state requested
        if state_id:
            state = get_object_or_404(State, id=state_id)
            return Response({
                "id": state.id,
                "name": state.name,
                # "latitude": state.latitude,
                # "longitude": state.longitude
            })

        # 🔹 If no state_id → return all states
        states = State.objects.all().order_by("name")

        return Response([
            {
                "id": s.id,
                "name": s.name,
            }
            for s in states
        ])
        
        
class DistrictByStateAPI(APIView):

    def get(self, request, state_id):

        # 🔹 Get state
        state = get_object_or_404(State, id=state_id)

        # 🔹 Get districts of that state
        districts = District.objects.filter(state_id=state_id)

        district_list = [
            {
                "district_id": d.id,
                "district_name": d.name
            }
            for d in districts
        ]

        return Response({
            "state_id": state.id,
            "state_name": state.name,
            "district_count": districts.count(),
            "districts": district_list
        })

class SubDistrictByDistrictAPI(APIView):

    def get(self, request, district_id):

        # 🔹 Get district
        district = get_object_or_404(District.objects.select_related("state"), id=district_id)

        # 🔹 Get subdistricts
        subs = SubDistrict.objects.filter(district_id=district_id)

        sub_list = [
            {
                "subdistrict_id": s.id,
                "subdistrict_name": s.name
            }
            for s in subs
        ]

        return Response({
            "state_id": district.state.id,
            "state_name": district.state.name,
            "district_id": district.id,
            "district_name": district.name,
            "subdistrict_count": subs.count(),
            "subdistricts": sub_list
        })

class TownBySubDistrictAPI(APIView):

    def get(self, request, subdistrict_id):

        subdistrict = get_object_or_404(
            SubDistrict.objects.select_related("district__state"),
            id=subdistrict_id
        )

        towns = Town.objects.filter(subdistrict_id=subdistrict_id)

        town_list = []

        for t in towns:
            town_list.append({
                "town_id": t.id,
                "town_name": t.name,   # ✅ Direct name field
                "latitude": t.latitude,
                "longitude": t.longitude
            })

        return Response({
            "state_id": subdistrict.district.state.id,
            "state_name": subdistrict.district.state.name,

            "district_id": subdistrict.district.id,
            "district_name": subdistrict.district.name,

            "subdistrict_id": subdistrict.id,
            "subdistrict_name": subdistrict.name,

            "town_count": towns.count(),
            "towns": town_list
        })



class LocationHierarchyAPI(APIView):

    def get(self, request):

        state_id = request.query_params.get("state_id")
        district_id = request.query_params.get("district_id")

        # 🔹 If district_id provided
        if district_id:
            district = District.objects.filter(id=district_id).first()
            if not district:
                return Response({"error": "District not found"})
            serializer = DistrictSerializer(district)
            return Response(serializer.data)

        # 🔹 If state_id provided
        if state_id:
            state = State.objects.filter(id=state_id).first()
            if not state:
                return Response({"error": "State not found"})
            serializer = StateSerializer(state)
            return Response(serializer.data)

        # 🔹 If nothing provided → return all
        states = State.objects.all()
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)


class StatedbListAPI(APIView):
    def get(self, request, state_id=None):

        # 🔹 If specific state requested
        if state_id:
            state = get_object_or_404(Statedb, id=state_id)
            return Response({
                "id": state.id,
                "name": state.name,
                # "latitude": state.latitude,
                # "longitude": state.longitude
            })

        # 🔹 If no state_id → return all states
        states = Statedb.objects.all().order_by("name")

        return Response([
            {
                "id": s.id,
                "name": s.name,
                "latitude":s.latitude,
                "longitude":s.longitude
            }
            for s in states
        ])
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from survey_app.models import Districtdb
from survey_app.serializers import DistrictdbSerializer


class DistrictdbCRUDAPI(APIView):

    # 🔹 READ (All or Single)
    def get(self, request, pk=None):

        if pk:
            district = get_object_or_404(Districtdb, pk=pk)
            serializer = DistrictdbSerializer(district)
            return Response(serializer.data)

        districts = Districtdb.objects.all()
        serializer = DistrictdbSerializer(districts, many=True)
        return Response(serializer.data)

    # 🔹 CREATE
    def post(self, request):
        serializer = DistrictdbSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 UPDATE
    # def put(self, request, pk):
    #     district = get_object_or_404(Districtdb, pk=pk)
    #     serializer = DistrictdbSerializer(district, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # 🔹 DELETE
    # def delete(self, request, pk):
    #     district = get_object_or_404(Districtdb, pk=pk)
    #     district.delete()
    #     return Response(
    #         {"message": "District deleted successfully"},
    #         status=status.HTTP_204_NO_CONTENT
    #     )
        
class DistrictdbByStateAPI(APIView):

    def get(self, request, state_id):

        # 🔹 Get state
        state = get_object_or_404(Statedb, id=state_id)

        # 🔹 Get districts of that state
        districts = Districtdb.objects.filter(state_id=state_id)

        district_list = [
            {
                "district_id": d.id,
                "district_name": d.name,
                "latitude":d.latitude,
                "longitude":d.longitude
            }
            for d in districts
        ]

        return Response({
            "state_id": state.id,
            "state_name": state.name,
            "latitude":state.latitude,
            "longitude":state.longitude,
            "district_count": districts.count(),
            "districts": district_list
        })
class StationdbByDistrictAPI(APIView):

    def get(self, request, district_id):

        # 🔹 Get district
        district = get_object_or_404(Districtdb.objects.select_related("state"), id=district_id)

        # 🔹 Get subdistricts
        subs = Stationdb.objects.filter(district_id=district_id)

        sub_list = [
            {
                "station_id": s.id,
                "station_name": s.name,
                "latitude":s.latitude,
                "longitude":s.longitude
            }
            for s in subs
        ]

        return Response({
            "state_id": district.state.id,
            "state_name": district.state.name,
            "district_id": district.id,
            "district_name": district.name,
            "station": subs.count(),
            "station": sub_list
        })

class StationdbCRUDAPI(APIView):

    # 🔹 READ (All or Single)
    def get(self, request, pk=None):

        if pk:
            station = get_object_or_404(Stationdb, pk=pk)
            serializer = StationdbSerializer(station)
            return Response(serializer.data)

        stations = Stationdb.objects.all()
        serializer = StationdbSerializer(stations, many=True)
        return Response(serializer.data)

    # 🔹 CREATE
    def post(self, request):
        serializer = StationdbSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 🔹 UPDATE
    # def put(self, request, pk):
    #     station = get_object_or_404(Stationdb, pk=pk)
    #     serializer = StationdbSerializer(station, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # 🔹 DELETE
    # def delete(self, request, pk):
    #     station = get_object_or_404(Stationdb, pk=pk)
    #     station.delete()
    #     return Response(
    #         {"message": "Station deleted successfully"},
    #         status=status.HTTP_204_NO_CONTENT
    #     )


