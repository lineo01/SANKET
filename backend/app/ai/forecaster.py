import math
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.db_models import RiverReading, SensorReading

class HydrologicalForecaster:
    """
    Time-Series Crest & Lead-Time Forecaster.
    Resiliently handles 1, 2, or multi-point hydrograph time-series without crashing.
    """
    def __init__(self, warning_level_m: float = 5.0, danger_level_m: float = 5.4):
        self.warning_level = warning_level_m
        self.danger_level = danger_level_m

    def predict_crest(self, river_history: List[RiverReading], sensor_history: List[SensorReading] = None) -> Dict[str, Any]:
        # Fallback if table is completely empty
        if not river_history or len(river_history) == 0:
            current_level = 2.40
            return {
                "current_water_level_m": 2.40,
                "rate_of_rise_m_per_hr": 0.0,
                "acceleration_m_per_hr2": 0.0,
                "predicted_crest_m": 2.40,
                "quantile_p10_m": 2.20,
                "quantile_p90_m": 2.60,
                "time_to_crest_hours": 0.0,
                "lead_time_to_danger_hours": None,
                "trend": "steady",
                "severity": "NORMAL",
                "forecast_generated_at": datetime.utcnow().isoformat()
            }

        sorted_readings = sorted(river_history, key=lambda r: r.timestamp)
        n = len(sorted_readings)
        current = sorted_readings[-1]
        current_level = current.water_level_m

        # Derivative calculation based on available points
        if n >= 3:
            prev_1 = sorted_readings[-2]
            prev_2 = sorted_readings[-3]
            dt1_hrs = max(0.05, (current.timestamp - prev_1.timestamp).total_seconds() / 3600.0)
            dt2_hrs = max(0.05, (prev_1.timestamp - prev_2.timestamp).total_seconds() / 3600.0)
            v1 = (current.water_level_m - prev_1.water_level_m) / dt1_hrs
            v2 = (prev_1.water_level_m - prev_2.water_level_m) / dt2_hrs
            acceleration = (v1 - v2) / ((dt1_hrs + dt2_hrs) / 2.0)
        elif n == 2:
            prev_1 = sorted_readings[-2]
            dt1_hrs = max(0.05, (current.timestamp - prev_1.timestamp).total_seconds() / 3600.0)
            v1 = (current.water_level_m - prev_1.water_level_m) / dt1_hrs
            acceleration = 0.0
        else:
            v1 = 0.0
            acceleration = 0.0

        # Sensor rainfall integration
        rainfall_modifier = 0.0
        if sensor_history and len(sensor_history) > 0:
            recent_rain = sensor_history[-1].rainfall_mm_per_hr or 0.0
            rainfall_modifier = min(0.4, (recent_rain / 100.0) * 0.35)

        # Crest & Trend estimation
        if v1 > 0.02:
            estimated_peak_decay = max(0.08, abs(acceleration) if acceleration < 0 else 0.12)
            time_to_peak_hrs = min(12.0, max(1.0, v1 / estimated_peak_decay))
            crest_surge = (v1 * time_to_peak_hrs) - (0.5 * estimated_peak_decay * (time_to_peak_hrs ** 2))
            predicted_crest_m = round(current_level + max(0.05, crest_surge) + rainfall_modifier, 2)
            trend_label = "rising"
        elif v1 < -0.02:
            time_to_peak_hrs = 0.0
            predicted_crest_m = current_level
            trend_label = "falling"
        else:
            time_to_peak_hrs = 0.0
            predicted_crest_m = current_level
            trend_label = "steady"

        # Uncertainty intervals
        uncertainty_margin = round(0.12 + (0.05 * time_to_peak_hrs), 2)
        p10 = round(predicted_crest_m - uncertainty_margin, 2)
        p90 = round(predicted_crest_m + uncertainty_margin, 2)

        # Lead time
        if current_level < self.danger_level and v1 > 0:
            lead_time_to_danger_hrs = round((self.danger_level - current_level) / v1, 1)
        elif current_level >= self.danger_level:
            lead_time_to_danger_hrs = 0.0
        else:
            lead_time_to_danger_hrs = None

        # Severity Classification
        if predicted_crest_m >= self.danger_level + 0.5:
            severity = "CRITICAL"
        elif predicted_crest_m >= self.danger_level:
            severity = "DANGER"
        elif predicted_crest_m >= self.warning_level:
            severity = "WARNING"
        else:
            severity = "NORMAL"

        return {
            "current_water_level_m": current_level,
            "rate_of_rise_m_per_hr": round(v1, 3),
            "acceleration_m_per_hr2": round(acceleration, 3),
            "predicted_crest_m": predicted_crest_m,
            "quantile_p10_m": p10,
            "quantile_p90_m": p90,
            "time_to_crest_hours": round(time_to_peak_hrs, 1),
            "lead_time_to_danger_hours": lead_time_to_danger_hrs,
            "trend": trend_label,
            "severity": severity,
            "forecast_generated_at": datetime.utcnow().isoformat()
        }
