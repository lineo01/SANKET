from typing import List, Dict, Any

class EvacuationTriageEngine:
    """
    Multi-Criteria Evacuation Prioritization Engine.
    Computes an Evacuation Priority Index (EPI) to rank households for rescue teams.
    """
    BUILDING_FRAGILITY = {
        "kachha": 2.2,
        "semi-pakka": 1.4,
        "pakka": 1.0
    }

    def rank_households(self, assessed_households: List[Dict[str, Any]], lead_time_hrs: float) -> List[Dict[str, Any]]:
        ranked = []

        for h in assessed_households:
            depth = h["predicted_water_depth_m"]
            b_fragility = self.BUILDING_FRAGILITY.get(h["building_type"].lower(), 1.2)
            
            vuln_score = (
                (h.get("elderly", 0) * 1.5) +
                (h.get("children", 0) * 1.2) +
                (h.get("disabled", 0) * 2.8) +
                (h.get("pregnant", 0) * 2.2) +
                (3.5 if h.get("medical_dependency") else 0.0) +
                (h.get("residents", 1) * 0.3)
            )

            hazard_index = depth * 3.5
            time_urgency = max(1.0, 5.0 - (lead_time_hrs if lead_time_hrs is not None else 3.0))

            if depth > 0:
                epi = round((hazard_index * b_fragility) + (vuln_score * 1.8) + time_urgency, 2)
            else:
                epi = round(vuln_score * 0.1, 2)

            if epi >= 20.0:
                priority = "IMMEDIATE_EVACUATION"
            elif epi >= 10.0:
                priority = "HIGH_PRIORITY"
            elif epi > 2.0:
                priority = "MONITOR"
            else:
                priority = "SAFE"

            h_copy = dict(h)
            h_copy["evacuation_priority_index"] = epi
            h_copy["priority_level"] = priority
            ranked.append(h_copy)

        ranked.sort(key=lambda x: x["evacuation_priority_index"], reverse=True)
        return ranked
