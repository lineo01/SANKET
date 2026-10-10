import math
from typing import List, Dict, Any, Optional
from app.models.db_models import Household

class InundationSurrogate:
    """
    Physics-Informed Hydrodynamic Surrogate Model (PI-HSM).
    Models 2D floodplain attenuation, Manning roughness, DEFRA Hazard Ratings,
    and structural collapse shear thresholds.
    """
    # Manning roughness coefficients (n) for Terai landcover
    MANNING_N = {
        "Kusum Floodplain": 0.055,      # Heavy brush, agricultural floodplain
        "Kusum Lower": 0.045,           # Scattered brush, rural settlement
        "Kusum Mid-Ward": 0.038,        # Dirt roads, compacted soil
        "Agaiya Transition": 0.035,     # Sparse vegetation, gravel
        "Agaiya High Ground": 0.030     # Paved, elevated ridge
    }

    # Plinth height baselines above local DEM grade (meters)
    PLINTH_HEIGHT_M = {
        "kachha": 0.12,        # Low mud plinth (highly vulnerable to overtopping)
        "semi-pakka": 0.28,    # Brick/cement-raised plinth
        "pakka": 0.45          # Concrete elevated slab
    }

    def __init__(self, gauge_base_elevation_m: float = 145.0, valley_slope: float = 0.00075):
        self.gauge_datum = gauge_base_elevation_m
        self.slope = valley_slope  # West Rapti bed slope (~0.75m per km)

    def assess_households(
        self,
        households: List[Household],
        predicted_crest_stage_m: float,
        ambient_humidity_percent: float = 80.0
    ) -> List[Dict[str, Any]]:
        results = []
        river_surface_elv = self.gauge_datum + predicted_crest_stage_m

        # Soil Saturation Modifier derived from DHT11 humidity
        # High humidity (>80%) = zero infiltration capacity, amplifying flood ponding
        saturation_factor = 1.0 + max(0.0, (ambient_humidity_percent - 70.0) / 100.0) * 0.15

        for hh in households:
            dist_km = hh.distance_to_river_m / 1000.0
            
            # 1. Hydraulic Backwater Attenuation
            # Flood surface drops longitudinally and experiences friction decay
            manning_n = self.MANNING_N.get(hh.zone, 0.045)
            friction_decay = (self.slope * dist_km * 0.6) + (manning_n * dist_km * 0.1)
            local_water_surface_m = river_surface_elv - friction_decay

            # 2. Outdoor Ground Flood Depth
            ground_depth_m = max(0.0, round((local_water_surface_m - hh.elevation_m) * saturation_factor, 2))

            # 3. Indoor Inundation Depth (accounting for building plinth elevation)
            plinth_m = self.PLINTH_HEIGHT_M.get(hh.building_type.lower(), 0.20)
            indoor_depth_m = max(0.0, round(ground_depth_m - plinth_m, 2))

            # 4. Manning-derived Flow Velocity Approximation (m/s)
            # v = (1/n) * (R^(2/3)) * (S^(1/2))
            if ground_depth_m > 0:
                hydraulic_radius = ground_depth_m  # Wide floodplain approximation
                velocity_mps = round((1.0 / manning_n) * (hydraulic_radius ** (2.0 / 3.0)) * math.sqrt(self.slope), 2)
            else:
                velocity_mps = 0.0

            # 5. International DEFRA Flood Hazard Rating (HR)
            # HR = d * (v + 0.5) + DF (Debris Factor)
            debris_factor = 0.5 if ground_depth_m <= 0.25 else 1.0
            if ground_depth_m > 0:
                hazard_rating = round((ground_depth_m * (velocity_mps + 0.5)) + debris_factor, 2)
            else:
                hazard_rating = 0.0

            # 6. Structural Hydrodynamic Collapse Check
            # Mud/Kachha structures collapse when depth > 0.8m OR shear energy d*v > 0.45 m^2/s
            b_type = hh.building_type.lower()
            structural_collapse_threat = False
            if ground_depth_m > 0:
                if b_type == "kachha" and (ground_depth_m >= 0.8 or (ground_depth_m * velocity_mps) >= 0.35):
                    structural_collapse_threat = True
                elif b_type == "semi-pakka" and (ground_depth_m >= 1.4 or (ground_depth_m * velocity_mps) >= 0.70):
                    structural_collapse_threat = True

            # Inundation Categorization
            if hazard_rating >= 2.0 or structural_collapse_threat:
                status = "DANGER_COLLAPSE_RISK"
            elif ground_depth_m >= 1.0:
                status = "DEEP_INUNDATION"
            elif ground_depth_m >= 0.3:
                status = "MODERATE_INUNDATION"
            elif ground_depth_m > 0.0:
                status = "SHALLOW_PONDING"
            else:
                status = "DRY"

            results.append({
                "household_id": hh.household_id,
                "ward": hh.ward,
                "zone": hh.zone,
                "residents": hh.residents,
                "building_type": hh.building_type,
                "elevation_m": hh.elevation_m,
                "distance_to_river_m": hh.distance_to_river_m,
                "nearest_shelter": hh.nearest_shelter,
                "phone_number": hh.phone_number,
                "predicted_water_depth_m": ground_depth_m,
                "indoor_depth_m": indoor_depth_m,
                "flow_velocity_mps": velocity_mps,
                "hazard_rating_hr": hazard_rating,
                "structural_collapse_threat": structural_collapse_threat,
                "inundation_status": status,
                "is_inundated": ground_depth_m > 0.0
            })

        return results
