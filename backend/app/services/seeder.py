import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.db_models import Household, RiverReading, SensorReading

def seed_database_from_json(db: Session) -> dict:
    data_dir = settings.SHARED_DATA_DIR

    # 1. Households GeoJSON
    hh_file = data_dir / "households.geojson"
    hh_count = 0
    if hh_file.exists():
        with open(hh_file, "r", encoding="utf-8") as f:
            hh_geojson = json.load(f)
            for feat in hh_geojson.get("features", []):
                p = feat["properties"]
                existing = db.query(Household).filter_by(household_id=p["household_id"]).first()
                if not existing:
                    household = Household(
                        household_id=p["household_id"],
                        zone=p["zone"],
                        ward=p["ward"],
                        latitude=p["latitude"],
                        longitude=p["longitude"],
                        elevation_m=p["elevation_m"],
                        residents=p["residents"],
                        elderly=p["elderly"],
                        children=p["children"],
                        disabled=p["disabled"],
                        pregnant=p["pregnant"],
                        medical_dependency=p["medical_dependency"],
                        building_type=p["building_type"],
                        distance_to_river_m=p["distance_to_river_m"],
                        nearest_shelter=p["nearest_shelter"],
                        phone_number=p.get("phone_number"),
                        app_registered=p.get("app_registered", False),
                    )
                    db.add(household)
                    hh_count += 1

    # 2. DHM River Readings
    dhm_file = data_dir / "sample_dhm_readings.json"
    dhm_count = 0
    if dhm_file.exists():
        with open(dhm_file, "r", encoding="utf-8") as f:
            readings = json.load(f)
            for r in readings:
                ts = datetime.fromisoformat(r["timestamp"])
                existing = db.query(RiverReading).filter_by(station_id=r["station_id"], timestamp=ts).first()
                if not existing:
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

    # 3. LoRa Sensor Readings
    sensor_file = data_dir / "sample_lora_readings.json"
    sensor_count = 0
    if sensor_file.exists():
        with open(sensor_file, "r", encoding="utf-8") as f:
            s_readings = json.load(f)
            for s in s_readings:
                ts = datetime.fromisoformat(s["timestamp"])
                existing = db.query(SensorReading).filter_by(node_id=s["node_id"], timestamp=ts).first()
                if not existing:
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
        "seeded_households": hh_count,
        "seeded_river_readings": dhm_count,
        "seeded_sensor_readings": sensor_count
    }
