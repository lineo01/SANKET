from typing import List, Dict, Any
from app.models.db_models import Household

class InundationSurrogate:
    """
    Sub-second physics-informed hydrodynamic surrogate model.
    Predicts household doorstep water depth based on gauge crest stage, DEM elevation,
    and reach slope decay.
    """
    def __init__(self, gauge_base_elevation_m: float = 145.0, hydraulic_slope: float = 0.00075):
        self.gauge_datum = gauge_base_elevation_m
        self.slope = hydraulic_slope

    def assess_households(self, households: List[Household], predicted_crest_stage_m: float) -> List[Dict[str, Any]]:
        results = []
        river_surface_elv = self.gauge_datum + predicted_crest_stage_m

        for hh in households:
            surface_drop = self.slope * (hh.distance_to_river_m / 1000.0)
            local_water_surface_m = river_surface_elv - surface_drop
            depth_m = max(0.0, round(local_water_surface_m - hh.elevation_m, 2))

            if depth_m > 1.2:
                status = "DEEP_INUNDATION"
            elif depth_m > 0.5:
                status = "MODERATE_INUNDATION"
            elif depth_m > 0.0:
                status = "SHALLOW_FLOODING"
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
                "predicted_water_depth_m": depth_m,
                "inundation_status": status,
                "is_inundated": depth_m > 0.0
            })

        return results
