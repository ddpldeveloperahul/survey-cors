from django.contrib import admin
from .models import *
from .models import User


# class UserAdminForm(forms.ModelForm):

#     class Meta:
#         model = User
#         fields = "__all__"

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # agar zone selected hai to us zone ke directors dikhaye
#         if "zone" in self.data:
#             zone = self.data.get("zone")

#             self.fields["director"].queryset = User.objects.filter(
#                 role="DIRECTOR",
#                 zone=zone
#             )

#         # edit mode me
#         elif self.instance.pk and self.instance.zone:
#             self.fields["director"].queryset = User.objects.filter(
#                 role="DIRECTOR",
#                 zone=self.instance.zone
#             )

#         else:
#             self.fields["director"].queryset = User.objects.filter(
#                 role="DIRECTOR"
#             )


# class UserAdmin(admin.ModelAdmin):

#     form = UserAdminForm

#     list_display = [
#         "username",
#         "name",
#         "email",
#         "role",
#         "zone",
#         "director",
#         "is_approved"
#     ]

#     list_filter = ["role", "zone", "is_approved"]


# admin.site.register(User, UserAdmin)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ("id", "email", "name", "role", "zone", "is_staff", "is_active","is_approved", "created_at")
#     search_fields = ("email", "name", "role", "zone")
#     list_filter = ("role", "zone", "is_staff", "is_active")

from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "username",
        "name",
        "email",
        "role",
        "zone",
        "director",
        "is_approved",
        "is_staff",
        "is_active",
        "created_at"
    ]

    list_filter = ["role", "zone", "is_approved"]
    search_fields = ("email", "name", "role", "zone")
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "director":
            kwargs["queryset"] = User.objects.filter(role="DIRECTOR")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(User, UserAdmin)
# class SurveyPhotoInline(admin.TabularInline):
#     model = SurveyPhoto
#     extra = 4

# @admin.register(Survey)
# class SurveyAdmin(admin.ModelAdmin):
#     list_display = ("id", "site_name", "surveyor", "remarks","status", "created_at")
#     inlines = [SurveyPhotoInline]
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("id", "station", "surveyor", "remarks","status")

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
# admin.site.register(SurveyApproval)
admin.site.register(State)
admin.site.register(District)   
admin.site.register(SubDistrict)
admin.site.register(Town)


@admin.register(SurveyApproval)
class SurveyApprovalAdmin(admin.ModelAdmin):
    list_display = ("id", "survey", "approval_level", "approved_by", "decision", "remarks", "approved_at")

admin.site.register(Statedb)
admin.site.register(Districtdb)
admin.site.register(Stationdb)