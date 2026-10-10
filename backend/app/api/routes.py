from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import Household, RiverReading, SensorReading
from app.models.schemas import (
    HouseholdSchema,
    RiverReadingSchema,
    SensorReadingSchema,
    HealthResponse
)
from app.services.seeder import seed_database_from_json

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    hh_count = db.query(Household).count()
    rr_count = db.query(RiverReading).count()
    sr_count = db.query(SensorReading).count()
    return {
        "status": "online",
        "database": "sqlite_connected",
        "household_count": hh_count,
        "river_readings_count": rr_count,
        "sensor_readings_count": sr_count
    }

@router.get("/households", response_model=List[HouseholdSchema])
def get_households(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Household).offset(skip).limit(limit).all()

@router.get("/river/readings", response_model=List[RiverReadingSchema])
def get_river_readings(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(RiverReading).order_by(RiverReading.timestamp.desc()).limit(limit).all()

@router.get("/sensors/readings", response_model=List[SensorReadingSchema])
def get_sensor_readings(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(limit).all()

@router.post("/data/seed")
def seed_data(db: Session = Depends(get_db)):
    return seed_database_from_json(db)
