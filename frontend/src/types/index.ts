export interface HealthStatus {
  status: string;
  database: string;
  household_count: number;
  river_readings_count: number;
  sensor_readings_count: number;
}

export interface HardwareSensorData {
  node_id?: string;
  water_raw?: number;
  water_level_cm?: number;
  simulated_river_m?: number;
  temperature_c?: number;
  humidity_percent?: number;
  connected?: boolean;
  port?: string;
  timestamp?: string;
}

export interface Rescuer {
  rescuer_id: string;
  name: string;
  name_en: string;
  org: string;
  phone: string;
  equipment: string;
  equipment_en: string;
}

export interface TriageHousehold {
  household_id: string;
  zone: string;
  head_of_household?: string;
  vulnerability_details?: string;
  latitude?: number;
  longitude?: number;
  residents: number;
  building_type: string;
  elevation_m: number;
  distance_to_river_m: number;
  nearest_shelter: string;
  phone_number: string;
  predicted_water_depth_m: number;
  indoor_depth_m?: number;
  flow_velocity_mps?: number;
  hazard_rating_hr?: number;
  structural_collapse_threat?: boolean;
  elderly: number;
  children: number;
  disabled: number;
  pregnant: number;
  medical_dependency: boolean;
  evacuation_priority_index: number;
  priority_level: string;
  alert_sms?: string;
  alert_engine?: string;
  assigned_rescuer?: Rescuer | null;
}

export interface VolunteerDispatch {
  household_id: string;
  head_of_household: string;
  vulnerability_details: string;
  predicted_water_depth_m: number;
  shelter: string;
  rescuer: Rescuer;
}

export interface AIAssessmentResponse {
  status: string;
  assessment_id: string;
  hardware_sensor?: HardwareSensorData;
  forecast: {
    current_water_level_m: number;
    predicted_crest_m: number;
    quantile_p90_m: number;
    severity: string;
    trend: string;
  };
  total_households_evaluated: number;
  inundated_households_count: number;
  evacuation_queue: TriageHousehold[];
  volunteer_dispatches: VolunteerDispatch[];
  queued_alert_payloads: Array<{
    household_id: string;
    head_of_household: string;
    phone_number: string;
    sms: string;
    engine: string;
    priority: string;
    assigned_rescuer?: Rescuer;
  }>;
}
