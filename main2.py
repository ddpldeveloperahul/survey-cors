# import os
# import django
# import pandas as pd
# import re

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
# django.setup()

# from survey_app.models import Statedb, Districtdb, Stationdb

# file_path = r"C:\Users\Dell Pc\Desktop\survey\s_r_a_a_b\CORS_COMPILED_DATA (1).xlsx"

# df = pd.read_excel(file_path)
# df.columns = df.columns.str.strip()
# df = df.where(pd.notnull(df), None)

# print("Detected Columns:", df.columns.tolist())

# for _, row in df.iterrows():

#     sl_no = row["Sl_No_"]                # ✅ FIXED
#     station_name = str(row["NAME"]).strip()
#     code = str(row["CODE"]).strip() if row["CODE"] else None
#     state_name = str(row["STATE"]).strip()
#     district_name = str(row["DISTRICT"]).strip()
#     latitude = row["LATITUDE"]
#     longitude = row["LONGITUDE"]
#     height = row["E_HEIGHT"]             # ✅ FIXED

#     state_obj, _ = Statedb.objects.get_or_create(name=state_name)

#     district_obj, _ = Districtdb.objects.get_or_create(
#         state=state_obj,
#         name=district_name
#     )

#     base_name = station_name

#     existing_names = Stationdb.objects.filter(
#         district=district_obj,
#         name__startswith=base_name
#     ).values_list("name", flat=True)

#     numbers = []

#     for name in existing_names:
#         match = re.match(rf"^{re.escape(base_name)}(?: (\d+))?$", name)
#         if match:
#             num = match.group(1)
#             numbers.append(int(num) if num else 0)

#     if numbers:
#         final_name = f"{base_name} {max(numbers)+1}"
#     else:
#         final_name = base_name

#     Stationdb.objects.create(
#         district=district_obj,
#         sl_no=sl_no,
#         name=final_name,
#         code=code,
#         latitude=latitude,
#         longitude=longitude,
#         height=height
#     )

# print("✅ Station data imported successfully")




import os
import django
import pandas as pd
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_r_a_a_b.settings")
django.setup()

from survey_app.models import Statedb, Districtdb, Stationdb

file_path = r"C:\Users\Dell Pc\Desktop\survey\s_r_a_a_b\CORS_COMPILED_DATA (1).xlsx"

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()
df = df.where(pd.notnull(df), None)

print("Detected Columns:", df.columns.tolist())

for _, row in df.iterrows():

    sl_no = row["Sl_No_"]
    station_name = str(row["NAME"]).strip()
    code = str(row["CODE"]).strip() if row["CODE"] else None
    state_name = str(row["STATE"]).strip()
    district_name = str(row["DISTRICT"]).strip()

    latitude = float(row["LATITUDE"]) if row["LATITUDE"] else None
    longitude = float(row["LONGITUDE"]) if row["LONGITUDE"] else None
    height = float(row["E_HEIGHT"]) if row["E_HEIGHT"] else None

    # ======================
    # STATE
    # ======================

    state_obj, created = Statedb.objects.get_or_create(
        name=state_name
    )

    # If lat/long NULL → update
    if state_obj.latitude is None and latitude:
        state_obj.latitude = latitude
        state_obj.longitude = longitude
        state_obj.save()

    # ======================
    # DISTRICT
    # ======================

    district_obj, created = Districtdb.objects.get_or_create(
        state=state_obj,
        name=district_name
    )

    if district_obj.latitude is None and latitude:
        district_obj.latitude = latitude
        district_obj.longitude = longitude
        district_obj.save()

    # ======================
    # STATION DUPLICATE HANDLING
    # ======================

    base_name = station_name

    existing_names = Stationdb.objects.filter(
        district=district_obj,
        name__startswith=base_name
    ).values_list("name", flat=True)

    numbers = []

    for name in existing_names:
        match = re.match(rf"^{re.escape(base_name)}(?: (\d+))?$", name)
        if match:
            num = match.group(1)
            numbers.append(int(num) if num else 0)

    if numbers:
        final_name = f"{base_name} {max(numbers) + 1}"
    else:
        final_name = base_name

    # ======================
    # CREATE STATION
    # ======================

    Stationdb.objects.create(
        district=district_obj,
        sl_no=sl_no,
        name=final_name,
        code=code,
        latitude=latitude,
        longitude=longitude,
        height=height
    )

print("✅ State, District & Station data imported successfully")