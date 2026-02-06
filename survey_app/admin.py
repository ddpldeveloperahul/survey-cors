from django.contrib import admin

from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "role", "zone", "is_staff", "is_active", "created_at")
    search_fields = ("email", "name", "role", "zone")
    list_filter = ("role", "zone", "is_staff", "is_active")


# class SurveyPhotoInline(admin.TabularInline):
#     model = SurveyPhoto
#     extra = 4

# @admin.register(Survey)
# class SurveyAdmin(admin.ModelAdmin):
#     list_display = ("id", "site_name", "surveyor", "remarks","status", "created_at")
#     inlines = [SurveyPhotoInline]
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("id", "site_name", "surveyor", "remarks","status")

# admin.site.register(SurveyPhoto)
@admin.register(SurveyPhoto)
class SurveyPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "sub_site", "north_photo", "east_photo", "south_photo", "west_photo", "captured_at")



admin.site.register(SurveySubSite)
# admin.site.register(User)
admin.site.register(SurveyLocation)
admin.site.register(SurveyMonument)
admin.site.register(SurveySkyVisibility)
admin.site.register(SurveyPower)
admin.site.register(SurveyConnectivity)
admin.site.register(SurveyApproval)

