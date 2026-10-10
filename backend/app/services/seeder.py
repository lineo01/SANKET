import json
import math
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import Base, engine
from app.models.db_models import Household, RiverReading, SensorReading

SHELTERS = [
    {"name": "श्री सरस्वती माध्यमिक विद्यालय", "coords": [81.8680, 28.0050]},
    {"name": "कुसुम स्वास्थ्य चौकी", "coords": [81.8825, 27.9940]},
    {"name": "वडा नं २ सामुदायिक भवन", "coords": [81.8755, 27.9985]},
    {"name": "नेपाल रेडक्रस बाढी उद्धार केन्द्र", "coords": [81.8890, 28.0035]}
]

PROFILES = [
    {"name": "रामबहादुर थापा", "note": "८२ वर्षीय खड्का थापा (अशक्त/अक्सिजन निर्भर)"},
    {"name": "सुनिता चौधरी", "note": "८ महिनाकी गर्भवती सुनिता र १ अपाङ्ग सदस्य"},
    {"name": "विक्रम दर्लामी", "note": "२ वृद्ध सदस्य र ह्विलचेयर निर्भर"},
    {"name": "लक्ष्मी परियार", "note": "३ साना बालबालिका (नवजात शिशु सहित)"},
    {"name": "धनीराम थारु", "note": "७८ वर्षीया आमा (दृष्टिविहीन)"},
    {"name": "कमला श्रेष्ठ", "note": "गर्भवती सदस्य र दमको बिरामी"},
    {"name": "टेकबहादुर पुन", "note": "शारीरिक अपाङ्गता भएका सदस्य"},
    {"name": "सीता वली", "note": "२ बालबालिका र १ वृद्ध आमा"},
    {"name": "प्रेमबहादुर भण्डारी", "note": "वृद्ध बाबु र नियमित डायलाइसिस"},
    {"name": "गीता खड्का", "note": "नवजात शिशु (२ महिना)"}
]

def get_nearest_shelter(lon: float, lat: float) -> str:
    best_name = SHELTERS[0]["name"]
    best_dist = 99999.0
    for s in SHELTERS:
        d = math.hypot(s["coords"][0] - lon, s["coords"][1] - lat)
        if d < best_dist:
            best_dist = d
            best_name = s["name"]
    return best_name

def seed_database_from_json(db: Session) -> dict:
    # 1. Cleanly recreate tables with latest schema to avoid SQLite column mismatches
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    data_dir = settings.SHARED_DATA_DIR
    hh_count = 0
    dhm_count = 0
    sensor_count = 0

    # 2. Seed 50 Households with Resident Names & Multi-Shelters
    hh_file = data_dir / "households.geojson"
    if hh_file.exists():
        with open(hh_file, "r", encoding="utf-8") as f:
            hh_geojson = json.load(f)
            for i, feat in enumerate(hh_geojson.get("features", [])):
                p = feat["properties"]
                coords = feat["geometry"]["coordinates"]
                lon, lat = coords[0], coords[1]
                
                profile = PROFILES[i % len(PROFILES)]
                shelter_assigned = get_nearest_shelter(lon, lat)

                has_vuln = (p.get("elderly", 0) > 0 or p.get("disabled", 0) > 0 or p.get("pregnant", 0) > 0 or p.get("medical_dependency", False))

                household = Household(
                    household_id=p["household_id"],
                    zone=p["zone"],
                    ward=p["ward"],
                    head_of_household=profile["name"],
                    vulnerability_details=profile["note"] if has_vuln else "सामान्य नागरिक",
                    latitude=lat,
                    longitude=lon,
                    elevation_m=p["elevation_m"],
                    residents=p["residents"],
                    elderly=p["elderly"],
                    children=p["children"],
                    disabled=p["disabled"],
                    pregnant=p["pregnant"],
                    medical_dependency=p.get("medical_dependency", False),
                    building_type=p["building_type"],
                    distance_to_river_m=p["distance_to_river_m"],
                    nearest_shelter=shelter_assigned,
                    phone_number=p.get("phone_number"),
                    app_registered=p.get("app_registered", False),
                )
                db.add(household)
                hh_count += 1

    # 3. Seed DHM Hydrograph Readings (Rising up to 6.3m)
    dhm_file = data_dir / "sample_dhm_readings.json"
    if dhm_file.exists():
        with open(dhm_file, "r", encoding="utf-8") as f:
            readings = json.load(f)
            for r in readings:
                ts = datetime.fromisoformat(r["timestamp"])
                rr = RiverReading(
                    station_id=r["station_id"],
                    station_name=r["station_name"],
                    district=r["district"],
                    basin=r["basin"],
                    water_level_m=r["water_level_m"],
                    warning_level_m=r["warning_level_m"],
                    danger_level_m=r["danger_level_m"],
                    trend=r["trend"],
                    discharge_m3s=r.get("discharge_m3s"),
                    source=r.get("source", "DHM"),
                    timestamp=ts
                )
                db.add(rr)
                dhm_count += 1

    # 4. Seed LoRa Sensor Readings
    sensor_file = data_dir / "sample_lora_readings.json"
    if sensor_file.exists():
        with open(sensor_file, "r", encoding="utf-8") as f:
            s_readings = json.load(f)
            for s in s_readings:
                ts = datetime.fromisoformat(s["timestamp"])
                sr = SensorReading(
                    node_id=s["node_id"],
                    water_level_cm=s["water_level_cm"],
                    rainfall_mm_per_hr=s["rainfall_mm_per_hr"],
                    temperature_c=s.get("temperature_c"),
                    humidity_percent=s.get("humidity_percent"),
                    battery_percent=s.get("battery_percent"),
                    timestamp=ts
                )
                db.add(sr)
                sensor_count += 1

    db.commit()
    return {
        "status": "success",
        "seeded_households": hh_count,
        "seeded_river_readings": dhm_count,
        "seeded_sensor_readings": sensor_count
    }
