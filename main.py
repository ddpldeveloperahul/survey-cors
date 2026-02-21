# import pandas as pd
# from survey_app.models import State, District, SubDistrict, Town
# import os
# import django

# file_path = r"C:\Users\Dell Pc\Downloads\survey (1)\survey\s_r_a_a_b\Priority 1_CORS Densification (5).xlsx"
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
# django.setup()
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




# import os
# import django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
# django.setup()

# import pandas as pd
# import re
# from survey_app.models import State, District, SubDistrict, Town

# file_path = r"C:\Users\Dell Pc\Downloads\survey (1)\survey\s_r_a_a_b\Priority 1_CORS Densification (5).xlsx"

# df = pd.read_excel(file_path)
# df.columns = df.columns.str.strip()

# for _, row in df.iterrows():

#     state_name = str(row["STATE_UT"]).strip()
#     district_name = str(row["DISTRICT"]).strip()
#     subdistrict_name = str(row["SUBDISTRICT"]).strip()
#     town_name = str(row["TOWN"]).strip()

#     town_lat = row["Lat"]
#     town_lon = row["Long"]

#     # 1️⃣ STATE
#     state_obj, _ = State.objects.get_or_create(name=state_name)

#     # 2️⃣ DISTRICT NUMBERING
#     district_pattern = rf"^{re.escape(district_name)}( \d+)?$"

#     district_count = District.objects.filter(
#         state=state_obj,
#         name__regex=district_pattern
#     ).count()

#     if district_count == 0:
#         district_final_name = district_name
#     else:
#         district_final_name = f"{district_name} {district_count}"

#     district_obj = District.objects.create(
#         state=state_obj,
#         name=district_final_name
#     )

#     # 3️⃣ SUBDISTRICT
#     subdistrict_obj, _ = SubDistrict.objects.get_or_create(
#         district=district_obj,
#         name=subdistrict_name
#     )

#     # 4️⃣ TOWN NUMBERING
#     town_pattern = rf"^{re.escape(town_name)}( \d+)?$"

#     town_count = Town.objects.filter(
#         subdistrict=subdistrict_obj,
#         name__regex=town_pattern
#     ).count()

#     if town_count == 0:
#         town_final_name = town_name
#     else:
#         town_final_name = f"{town_name} {town_count}"

#     Town.objects.create(
#         subdistrict=subdistrict_obj,
#         name=town_final_name,
#         latitude=town_lat,
#         longitude=town_lon
#     )

# print("✅ District and Town duplicate numbering completed successfully")



# import os
# import django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
# django.setup()

# import pandas as pd
# import re
# from survey_app.models import State, District, SubDistrict, Town

# file_path = r"C:\Users\Dell Pc\Downloads\survey (1)\survey\s_r_a_a_b\Priority 1_CORS Densification (5).xlsx"

# df = pd.read_excel(file_path)
# df.columns = df.columns.str.strip()

# for _, row in df.iterrows():

#     state_name = str(row["STATE_UT"]).strip()
#     district_name = str(row["DISTRICT"]).strip()
#     subdistrict_name = str(row["SUBDISTRICT"]).strip()
#     town_name = str(row["TOWN"]).strip()

#     town_lat = row["Lat"]
#     town_lon = row["Long"]

#     # 1️⃣ STATE
#     state_obj, _ = State.objects.get_or_create(name=state_name)

#     # 2️⃣ DISTRICT (No numbering now)
#     district_obj, _ = District.objects.get_or_create(
#         state=state_obj,
#         name=district_name
#     )

#     # 3️⃣ SUBDISTRICT
#     subdistrict_obj, _ = SubDistrict.objects.get_or_create(
#         district=district_obj,
#         name=subdistrict_name
#     )

#     # 4️⃣ TOWN NUMBERING ONLY
#     town_pattern = rf"^{re.escape(town_name)}( \d+)?$"

#     town_count = Town.objects.filter(
#         subdistrict=subdistrict_obj,
#         name__regex=town_pattern
#     ).count()

#     if town_count == 0:
#         town_final_name = town_name
#     else:
#         town_final_name = f"{town_name} {town_count}"

#     Town.objects.create(
#         subdistrict=subdistrict_obj,
#         name=town_final_name,
#         latitude=town_lat,
#         longitude=town_lon
#     )

# print("✅ Only Town duplicate numbering applied successfully")


# import os
# import django
# import pandas as pd

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
# django.setup()

# from survey_app.models import State, District, SubDistrict, Town

# file_path = r"C:\Users\dell\Downloads\survey\survey\s_r_a_a_b\Priority 1_CORS Densification.xlsx"

# df = pd.read_excel(file_path)
# df.columns = df.columns.str.strip()

# for _, row in df.iterrows():

#     state_name = str(row["STATE_UT"]).strip()
#     district_name = str(row["DISTRICT"]).strip()
#     subdistrict_name = str(row["SUBDISTRICT"]).strip()
#     town_name = str(row["TOWN"]).strip()

#     town_lat = row["Lat"]
#     town_lon = row["Long"]

#     # -------------------------
#     # 1️⃣ STATE
#     # -------------------------
#     state_obj, _ = State.objects.get_or_create(name=state_name)

#     # -------------------------
#     # 2️⃣ DISTRICT (Numbering)
#     # -------------------------
#     district_count = District.objects.filter(
#         state=state_obj,
#         name__startswith=district_name
#     ).count()

#     if district_count == 0:
#         district_final = district_name
#     else:
#         district_final = f"{district_name} {district_count}"

#     district_obj, _ = District.objects.get_or_create(
#         state=state_obj,
#         name=district_final
#     )

#     # -------------------------
#     # 3️⃣ SUBDISTRICT
#     # -------------------------
#     subdistrict_obj, _ = SubDistrict.objects.get_or_create(
#         district=district_obj,
#         name=subdistrict_name
#     )

#     # -------------------------
#     # 4️⃣ TOWN (PROPER NUMBERING)
#     # -------------------------

#     # Check exact duplicates inside same subdistrict
#     existing_same = Town.objects.filter(
#         subdistrict=subdistrict_obj,
#         name=town_name
#     ).exists()

#     if not existing_same:
#         final_town_name = town_name
#     else:
#         # Count how many similar towns exist
#         similar_count = Town.objects.filter(
#             subdistrict=subdistrict_obj,
#             name__startswith=town_name
#         ).count()

#         final_town_name = f"{town_name} {similar_count}"

#     Town.objects.create(
#         subdistrict=subdistrict_obj,
#         name=final_town_name,
#         latitude=town_lat,
#         longitude=town_lon
#     )

# print("✅ Import completed with correct duplicate numbering")





import os
import django
import pandas as pd
import re

# ==============================
# DJANGO SETUP
# ==============================

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
django.setup()

from survey_app.models import State, District, SubDistrict, Town

# ==============================
# FILE PATH
# ==============================

file_path = r"C:\Users\Dell Pc\Downloads\survey (1)\survey\s_r_a_a_b\Priority 1_CORS Densification (5).xlsx"

# ==============================
# READ EXCEL
# ==============================

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()
df = df.where(pd.notnull(df), None)

print("Columns detected:", df.columns.tolist())

# ==============================
# IMPORT DATA
# ==============================

for _, row in df.iterrows():

    state_name = str(row["STATE_UT"]).strip()
    district_name = str(row["DISTRICT"]).strip()
    subdistrict_name = str(row["SUBDISTRICT"]).strip()
    town_name = str(row["TOWN"]).strip()

    town_lat = row["Lat"]
    town_lon = row["Long"]

    # 1️⃣ STATE (No numbering)
    state_obj, _ = State.objects.get_or_create(name=state_name)

    # 2️⃣ DISTRICT (No numbering)
    district_obj, _ = District.objects.get_or_create(
        state=state_obj,
        name=district_name
    )

    # 3️⃣ SUBDISTRICT
    subdistrict_obj, _ = SubDistrict.objects.get_or_create(
        district=district_obj,
        name=subdistrict_name
    )

    # 4️⃣ TOWN NUMBERING (GENERIC FOR ANY RANDOM NAME)

    base_name = town_name

    # Find all towns with same base name in same subdistrict
    existing_names = Town.objects.filter(
        subdistrict=subdistrict_obj,
        name__startswith=base_name
    ).values_list("name", flat=True)

    numbers = []

    for name in existing_names:
        match = re.match(rf"^{re.escape(base_name)}(?: (\d+))?$", name)
        if match:
            num = match.group(1)
            numbers.append(int(num) if num else 0)

    if numbers:
        next_number = max(numbers) + 1
        final_name = f"{base_name} {next_number}"
    else:
        final_name = base_name

    Town.objects.create(
        subdistrict=subdistrict_obj,
        name=final_name,
        latitude=town_lat,
        longitude=town_lon
    )

print("✅ Import completed with automatic town duplicate numbering")