from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class HouseholdSchema(BaseModel):
    household_id: str
    zone: str
    ward: int
    latitude: float
    longitude: float
    elevation_m: float
    residents: int
    elderly: int
    children: int
    disabled: int
    pregnant: int
    medical_dependency: bool
    building_type: str
    distance_to_river_m: float
    nearest_shelter: str
    phone_number: Optional[str] = None
    app_registered: bool

    class Config:
        from_attributes = True


class RiverReadingSchema(BaseModel):
    station_id: str
    station_name: str
    district: str
    basin: str
    water_level_m: float
    warning_level_m: float
    danger_level_m: float
    trend: str
    discharge_m3s: Optional[float] = None
    source: str
    timestamp: datetime

    class Config:
        from_attributes = True


class SensorReadingSchema(BaseModel):
    node_id: str
    water_level_cm: float
    rainfall_mm_per_hr: float
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    battery_percent: Optional[float] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    database: str
    household_count: int
    river_readings_count: int
    sensor_readings_count: int
