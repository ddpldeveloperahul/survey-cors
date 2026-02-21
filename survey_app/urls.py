from django.urls import path
from .views import *



urlpatterns = [
    
    
    path("signup/", SignupAPI.as_view(), name="signup"),
    path("login/", LoginAPI.as_view(), name="login"),
    # SURVEYOR APIs
    # -------------------------
    # Create multiple sites (same user)
    path("survey/create_site/", SurveyCreateAPI.as_view(), name="survey-create"),
    path("survey/create_site/<uuid:survey_id>/", SurveyCreateAPI.as_view(), name="survey-create-id"),
    path("survey/create_site/<uuid:survey_id>/subsite/", SurveySubSiteCreateAPI.as_view(), name="survey-subsite-create"),
    path("survey/create_site/<uuid:survey_id>/subsite/<uuid:subsite_id>/", SurveySubSiteCreateAPI.as_view(), name="survey-subsite-create-id"),
    # Get survey details
    


    # -------------------------
    # SURVEY DATA APIs
    # -------------------------

    path("survey/subsite/<uuid:subsite_id>/location/",SurveyLocationAPI.as_view(),name="survey-location"),
    path("survey/subsite/<uuid:subsite_id>/location/<uuid:location_id>/",SurveyLocationAPI.as_view(),name="survey-location-id"),
    path("survey/subsite/<uuid:subsite_id>/monument/",SurveyMonumentAPI.as_view(),name="survey-monument"),
    path("survey/subsite/<uuid:subsite_id>/monument/<uuid:monument_id>/",SurveyMonumentAPI.as_view(),name="survey-monument-id"),
    path("survey/subsite/<uuid:subsite_id>/sky-visibility/",SurveySkyVisibilityAPI.as_view(),name="survey-sky-visibility"),
    path("survey/subsite/<uuid:subsite_id>/sky-visibility/<uuid:sky_visibility_id>/",SurveySkyVisibilityAPI.as_view(),name="survey-sky-visibility-id"),
    path("survey/subsite/<uuid:subsite_id>/power/",SurveyPowerAPI.as_view(),name="survey-power"),
    path("survey/subsite/<uuid:subsite_id>/power/<uuid:power_id>/",SurveyPowerAPI.as_view(),name="survey-power-id"),
    path("survey/subsite/<uuid:subsite_id>/connectivity/",SurveyConnectivityAPI.as_view(),name="survey-connectivity"),
    path("survey/subsite/<uuid:subsite_id>/connectivity/<uuid:connectivity_id>/",SurveyConnectivityAPI.as_view(),name="survey-connectivity-id"),
    path("survey/subsite/<uuid:subsite_id>/photo/",SurveyPhotoUploadAPI.as_view(),name="survey-photo"),
    path("survey/subsite/<uuid:subsite_id>/photo/<uuid:photo_id>/",SurveyPhotoUploadAPI.as_view(),name="survey-photo-id"),
    # Submit survey (lock)
    path("survey/create_site/<uuid:survey_id>/submit/",SurveySubmitAPI.as_view(),name="survey-submit"),

    # -------------------------
    # APPROVAL APIs (ALL ROLES)
    # -------------------------

    path(
    "survey/<uuid:survey_id>/approve/",
    SurveyApprovalAPI.as_view(),
    name="survey-approve"),
    
    path(
    "survey/<uuid:survey_id>/full_data/",
    SurveyFullDataAPI.as_view(),
    name="survey-full-data"
    ),
    path(
        "survey/my-sites/",
        SurveyListByUserAPI.as_view(),
        name="survey-my-sites"
    ),
    # -------------------------
    # DASHBOARD / LIST APIs
    # -------------------------
    # Role-wise pending list
    path("survey/pending/",PendingSurveyAPI.as_view(),name="survey-pending"),
    
    
    path("survey/map/", SurveyMapDataAPI.as_view()),
    path("survey/map/<uuid:location_id>/", SurveyMapDataAPI.as_view()),
    path("map/", survey_map_view, name="survey-map"),
    path("signup_front/", signup_view, name="signup"),
    path("login_front/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    
    path("users/", AllUsersAPI.as_view(), name="all-users"),
    path("users/role/<str:role>/", RoleWiseUsersAPI.as_view(), name="role-wise-users"),
  
    path("rinex/upload/", RinexUploadAPI.as_view(), name="rinex-upload"),
    path("rinex/upload/<uuid:file_id>/", RinexUploadAPI.as_view(), name="rinex-delete"),
    path("hierarchy/sites/", HierarchySurveyAPI.as_view(), name="hierarchy-sites"),
    
    
    # path("surveyforms/", create_survey, name="survey-forms"),
    path("states/", StateListAPI.as_view(), name="state-list"), 
    path("states/<int:state_id>/", StateListAPI.as_view(), name="state-detail"),
    path("districts/", DistrictByStateAPI.as_view(), name="district-list"), 
    path("states/<int:state_id>/districts/", DistrictByStateAPI.as_view()),
    path("districts/<int:district_id>/subdistricts/", SubDistrictByDistrictAPI.as_view()),
    path("subdistricts/<int:subdistrict_id>/towns/", TownBySubDistrictAPI.as_view()),
    path("location/", LocationHierarchyAPI.as_view()),
    
    path("statesdb/", StatedbListAPI.as_view(), name="statedb"),
    path("statesdb/<int:state_id>/", StatedbListAPI.as_view(), name="state-detail"),
    path("statesdb/<int:state_id>/districtsdb/", DistrictdbByStateAPI.as_view(), name="districtsdb"),
    path("districtsdb/<int:district_id>/stationdb/", StationdbByDistrictAPI.as_view(), name="stationdb"),
    
    
    
    
    #
]
