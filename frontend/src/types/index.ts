export interface HealthStatus {
  status: string;
  database: string;
  household_count: number;
  river_readings_count: number;
  sensor_readings_count: number;
}

export interface Household {
  household_id: string;
  zone: string;
  ward: number;
  latitude: number;
  longitude: number;
  elevation_m: number;
  residents: number;
  elderly: number;
  children: number;
  disabled: number;
  pregnant: number;
  medical_dependency: boolean;
  building_type: string;
  distance_to_river_m: number;
  nearest_shelter: string;
  phone_number?: string;
  app_registered: boolean;
}

export interface RiverReading {
  station_id: string;
  station_name: string;
  district: string;
  basin: string;
  water_level_m: number;
  warning_level_m: number;
  danger_level_m: number;
  trend: string;
  discharge_m3s?: number;
  source: string;
  timestamp: string;
}

export interface SensorReading {
  node_id: string;
  water_level_cm: number;
  rainfall_mm_per_hr: number;
  temperature_c?: number;
  humidity_percent?: number;
  battery_percent?: number;
  timestamp: string;
}
