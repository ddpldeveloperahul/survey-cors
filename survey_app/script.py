# import pandas as pd
# from survey_app.models import State, District, SubDistrict, Town

# file_path = r"C:\Users\dell\Downloads\survey\Priority 1_CORS Densification.xlsx"

# df = pd.read_excel(file_path)
# df.columns = df.columns.str.strip()

# for _, row in df.iterrows():

#     state_name = str(row["STATE_UT"]).strip()
#     district_name = str(row["DISTRICT"]).strip()
#     subdistrict_name = str(row["SUBDISTRICT"]).strip()
#     town_name = str(row["TOWN"]).strip()

#     town_lat = row["Lat"]
#     town_lon = row["Long"]

#     # 1️⃣ State
#     state_obj, _ = State.objects.get_or_create(name=state_name)

#     # 2️⃣ District with numbering if duplicate
#     existing_districts = District.objects.filter(
#         state=state_obj,
#         name__startswith=district_name
#     ).count()

#     if existing_districts > 0:
#         district_final_name = f"{district_name} {existing_districts + 1}"
#     else:
#         district_final_name = district_name

#     district_obj, _ = District.objects.get_or_create(
#         state=state_obj,
#         name=district_final_name
#     )

#     # 3️⃣ SubDistrict
#     subdistrict_obj, _ = SubDistrict.objects.get_or_create(
#         district=district_obj,
#         name=subdistrict_name
#     )

#     # 4️⃣ Town with numbering if duplicate
#     existing_towns = Town.objects.filter(
#         subdistrict=subdistrict_obj,
#         base_name__startswith=town_name
#     ).count()

#     if existing_towns > 0:
#         town_final_name = f"{town_name} {existing_towns + 1}"
#     else:
#         town_final_name = town_name

#     Town.objects.create(
#         subdistrict=subdistrict_obj,
#         base_name=town_final_name,
#         latitude=town_lat,
#         longitude=town_lon
#     )

# print("✅ All data imported successfully with duplicate numbering")
import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
django.setup()

from survey_app.models import State, District, SubDistrict, Town

file_path = r"C:\Users\dell\Downloads\survey\Priority 1_CORS Densification.xlsx"

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()

for _, row in df.iterrows():

    state_name = str(row["STATE_UT"]).strip()
    district_name = str(row["DISTRICT"]).strip()
    subdistrict_name = str(row["SUBDISTRICT"]).strip()
    town_name = str(row["TOWN"]).strip()

    town_lat = row["Lat"]
    town_lon = row["Long"]

    # 1️⃣ State
    state_obj, _ = State.objects.get_or_create(name=state_name)

    # 2️⃣ District numbering
    district_count = District.objects.filter(
        state=state_obj,
        name__startswith=district_name
    ).count()

    district_final_name = (
        f"{district_name} {district_count + 1}"
        if district_count > 0 else district_name
    )

    district_obj, _ = District.objects.get_or_create(
        state=state_obj,
        name=district_final_name
    )

    # 3️⃣ SubDistrict
    subdistrict_obj, _ = SubDistrict.objects.get_or_create(
        district=district_obj,
        name=subdistrict_name
    )

    # 4️⃣ Town numbering
    town_count = Town.objects.filter(
        subdistrict=subdistrict_obj,
        base_name__startswith=town_name
    ).count()

    town_final_name = (
        f"{town_name} {town_count + 1}"
        if town_count > 0 else town_name
    )

    Town.objects.create(
        subdistrict=subdistrict_obj,
        base_name=town_final_name,
        latitude=town_lat,
        longitude=town_lon
    )

print("✅ All data imported successfully with duplicate numbering")
