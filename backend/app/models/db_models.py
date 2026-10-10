from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from app.core.database import Base

class Household(Base):
    __tablename__ = "households"

    household_id = Column(String(32), primary_key=True, index=True)
    zone = Column(String(64), nullable=False)
    ward = Column(Integer, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=False)
    residents = Column(Integer, nullable=False, default=1)
    elderly = Column(Integer, nullable=False, default=0)
    children = Column(Integer, nullable=False, default=0)
    disabled = Column(Integer, nullable=False, default=0)
    pregnant = Column(Integer, nullable=False, default=0)
    medical_dependency = Column(Boolean, nullable=False, default=False)
    building_type = Column(String(32), nullable=False)
    distance_to_river_m = Column(Float, nullable=False)
    nearest_shelter = Column(String(128), nullable=False)
    phone_number = Column(String(20), nullable=True)
    app_registered = Column(Boolean, nullable=False, default=False)


class RiverReading(Base):
    __tablename__ = "river_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(32), index=True, nullable=False)
    station_name = Column(String(128), nullable=False)
    district = Column(String(64), nullable=False)
    basin = Column(String(64), nullable=False)
    water_level_m = Column(Float, nullable=False)
    warning_level_m = Column(Float, nullable=False)
    danger_level_m = Column(Float, nullable=False)
    trend = Column(String(16), nullable=False)
    discharge_m3s = Column(Float, nullable=True)
    source = Column(String(32), nullable=False, default="DHM")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(32), index=True, nullable=False)
    water_level_cm = Column(Float, nullable=False)
    rainfall_mm_per_hr = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    battery_percent = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class FloodAssessment(Base):
    __tablename__ = "flood_assessments"

    assessment_id = Column(String(36), primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    risk_level = Column(String(20), nullable=False)
    water_level_trend = Column(String(16), nullable=False)
    predicted_crest_m = Column(Float, nullable=True)
    lead_time_hours = Column(Float, nullable=True)
    details = Column(Text, nullable=True)


class AlertTarget(Base):
    __tablename__ = "alert_targets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String(36), ForeignKey("flood_assessments.assessment_id"), nullable=False)
    household_id = Column(String(32), ForeignKey("households.household_id"), nullable=False)
    channel = Column(String(20), nullable=False)
    delivery_status = Column(String(20), nullable=False, default="PENDING")
    queued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


class ResidentStatus(Base):
    __tablename__ = "resident_statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    household_id = Column(String(32), ForeignKey("households.household_id"), nullable=False)
    status = Column(String(32), nullable=False)
    current_location = Column(String(128), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
