import pandas as pd
from survey_app.models import State, District, SubDistrict, Town

file_path = r"C:\Users\Dell Pc\Desktop\survey\Priority 1_CORS Densification.xlsx"

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()

for _, row in df.iterrows():

    state_name = str(row["STATE_UT"]).strip()
    district_name = str(row["DISTRICT"]).strip()
    subdistrict_name = str(row["SUBDISTRICT"]).strip()
    town_name = str(row["TOWN"]).strip()

    # Get latitude & longitude (handle blank safely)
    state_lat = row.get("LATITUDE")
    state_lon = row.get("LONGITUDE")

    # 1️⃣ Create or Update State with lat/long
    state_obj, created = State.objects.get_or_create(
        name=state_name,
        defaults={
            "latitude": state_lat,
            "longitude": state_lon
        }
    )

    # If state already exists but lat/long empty, update it
    if not created:
        if not state_obj.latitude:
            state_obj.latitude = state_lat
        if not state_obj.longitude:
            state_obj.longitude = state_lon
        state_obj.save()

    # 2️⃣ District
    district_obj, _ = District.objects.get_or_create(
        state=state_obj,
        name=district_name
    )

    # 3️⃣ SubDistrict
    subdistrict_obj, _ = SubDistrict.objects.get_or_create(
        district=district_obj,
        name=subdistrict_name
    )

    # 4️⃣ Town
    Town.objects.create(
        subdistrict=subdistrict_obj,
        base_name=town_name
    )

print("✅ All data including State lat/long saved successfully")