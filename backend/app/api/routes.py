import json
import uuid
import traceback
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.db_models import Household, RiverReading, SensorReading, FloodAssessment, AlertTarget
from app.models.schemas import HouseholdSchema, RiverReadingSchema, SensorReadingSchema, HealthResponse
from app.services.seeder import seed_database_from_json
from app.services.dhm_scraper import DHMScraperService
from app.services.serial_bridge import ArduinoSerialBridge
from app.ai.forecaster import HydrologicalForecaster
from app.ai.surrogate import InundationSurrogate
from app.ai.triage import EvacuationTriageEngine
from app.ai.alert_generator import OllamaAlertGenerator

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    return {
        "status": "online",
        "database": "sqlite_connected",
        "household_count": db.query(Household).count(),
        "river_readings_count": db.query(RiverReading).count(),
        "sensor_readings_count": db.query(SensorReading).count()
    }

@router.get("/river/geojson")
def get_river_network_geojson():
    river_file = settings.SHARED_DATA_DIR / "river.geojson"
    if river_file.exists():
        with open(river_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}

@router.get("/shelters/geojson")
def get_shelters_geojson():
    shelter_file = settings.SHARED_DATA_DIR / "shelters.geojson"
    if shelter_file.exists():
        with open(shelter_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}

@router.get("/sensors/live-hardware")
def get_live_hardware_sensor():
    return ArduinoSerialBridge.latest_telemetry

@router.api_route("/data/seed", methods=["GET", "POST"])
def seed_data(db: Session = Depends(get_db)):
    return seed_database_from_json(db)

@router.api_route("/scraper/sync-dhm", methods=["GET", "POST"])
def sync_government_dhm(db: Session = Depends(get_db)):
    reading = DHMScraperService.scrape_real_government_reading(db)
    return {"status": "synced", "telemetry": reading}

@router.api_route("/ai/assess", methods=["GET", "POST"])
def run_full_flood_assessment(
    lang: str = Query("ne", pattern="^(ne|en)$"),
    drive_mode: str = Query("hardware", pattern="^(hardware|gov_only)$"),
    use_llm: bool = Query(True),
    db: Session = Depends(get_db)
):
    try:
        # Self-healing: If database is fresh and has no readings, seed baseline automatically
        if db.query(RiverReading).count() < 3 or db.query(Household).count() == 0:
            seed_database_from_json(db)

        households = db.query(Household).all()
        live_hw = ArduinoSerialBridge.latest_telemetry
        is_hw_active = live_hw.get("connected", False) and (live_hw.get("water_raw") is not None)
        ambient_humidity = float(live_hw.get("humidity_percent") or 80.0)

        # 1. Determine River Stage
        if drive_mode == "hardware" and is_hw_active:
            raw_val = float(live_hw["water_raw"])
            simulated_stage = round(2.20 + (raw_val / 650.0) * 4.30, 2)
            active_stage = min(6.60, simulated_stage)
            data_source = f"LIVE_ARDUINO_{live_hw.get('port')}"
        else:
            latest_dhm = db.query(RiverReading).order_by(RiverReading.timestamp.desc()).first()
            active_stage = latest_dhm.water_level_m if latest_dhm else 2.40
            data_source = "DHM_GOVERNMENT_BASELINE"

        # Record active reading
        db.add(RiverReading(
            station_id="DHM-430",
            station_name="Kusum",
            district="Banke",
            basin="West Rapti",
            water_level_m=active_stage,
            warning_level_m=5.00,
            danger_level_m=5.40,
            trend="rising" if active_stage >= 5.0 else "steady",
            discharge_m3s=round(active_stage * 210.0, 1),
            source=data_source
        ))
        db.commit()

        river_readings = db.query(RiverReading).order_by(RiverReading.timestamp.asc()).all()
        sensor_readings = db.query(SensorReading).order_by(SensorReading.timestamp.asc()).all()

        # 2. Time-Series Forecaster (Zero Crash Guarantee)
        forecaster = HydrologicalForecaster()
        forecast = forecaster.predict_crest(river_readings, sensor_readings)
        forecast["current_water_level_m"] = active_stage
        forecast["predicted_crest_m"] = active_stage

        # 3. Physics Inundation Surrogate
        surrogate = InundationSurrogate()
        inundated_hh = surrogate.assess_households(
            households=households,
            predicted_crest_stage_m=active_stage,
            ambient_humidity_percent=ambient_humidity
        )

        hh_map = {h.household_id: h for h in households}
        for h in inundated_hh:
            db_h = hh_map.get(h["household_id"])
            if db_h:
                h["head_of_household"] = db_h.head_of_household
                h["vulnerability_details"] = db_h.vulnerability_details
                h["nearest_shelter"] = db_h.nearest_shelter
                h["latitude"] = db_h.latitude
                h["longitude"] = db_h.longitude
                h["elderly"] = db_h.elderly
                h["children"] = db_h.children
                h["disabled"] = db_h.disabled
                h["pregnant"] = db_h.pregnant
                h["medical_dependency"] = db_h.medical_dependency

        # 4. Triage & Rescuer Allocation
        triage = EvacuationTriageEngine()
        ranked_households = triage.rank_households(inundated_hh, forecast["lead_time_to_danger_hours"])

        # 5. Alert Synthesis
        assessment_id = str(uuid.uuid4())
        alert_payloads = []
        volunteer_dispatches = []

        for i, h in enumerate(ranked_households):
            if h["priority_level"] in ["IMMEDIATE_EVACUATION", "HIGH_PRIORITY"]:
                res = OllamaAlertGenerator.generate_llm_alert(h, forecast, language=lang)
                h["alert_sms"] = res["alert_text"]
                h["alert_engine"] = res["engine"]

                if len(alert_payloads) < 5:
                    alert_payloads.append({
                        "household_id": h["household_id"],
                        "head_of_household": h.get("head_of_household"),
                        "phone_number": h["phone_number"],
                        "sms": res["alert_text"],
                        "engine": res["engine"],
                        "priority": h["priority_level"],
                        "assigned_rescuer": h.get("assigned_rescuer")
                    })

                if h.get("assigned_rescuer"):
                    volunteer_dispatches.append({
                        "household_id": h["household_id"],
                        "head_of_household": h.get("head_of_household"),
                        "vulnerability_details": h.get("vulnerability_details"),
                        "predicted_water_depth_m": h["predicted_water_depth_m"],
                        "shelter": h["nearest_shelter"],
                        "rescuer": h["assigned_rescuer"]
                    })

        result_payload = {
            "status": "success",
            "assessment_id": assessment_id,
            "data_source": data_source,
            "hardware_sensor": live_hw,
            "forecast": forecast,
            "total_households_evaluated": len(households),
            "inundated_households_count": sum(1 for h in ranked_households if h["is_inundated"]),
            "evacuation_queue": ranked_households,
            "volunteer_dispatches": volunteer_dispatches[:6],
            "queued_alert_payloads": alert_payloads
        }

        return Response(
            content=json.dumps(result_payload, ensure_ascii=False),
            media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        traceback.print_exc()
        return Response(
            content=json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=500
        )
