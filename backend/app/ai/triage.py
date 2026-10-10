from typing import List, Dict, Any

# Dedicated volunteer rescue units stationed in Rapti Sonari Ward 2
VOLUNTEER_UNITS = [
    {
        "rescuer_id": "VOL-01",
        "name": "सागर थापा",
        "name_en": "Sagar Thapa",
        "org": "नेपाल रेडक्रस (कुसुम एकाइ)",
        "phone": "9848112233",
        "equipment": "रबर बोट / लाइफ ज्याकेट",
        "equipment_en": "Inflatable Rescue Boat"
    },
    {
        "rescuer_id": "VOL-02",
        "name": "पूजा चौधरी",
        "name_en": "Pooja Chaudhary",
        "org": "विपद् व्यवस्थापन समिति",
        "phone": "9848223344",
        "equipment": "स्ट्रेचर र प्राथमिक उपचार किट",
        "equipment_en": "Stretcher & Emergency First Aid"
    },
    {
        "rescuer_id": "VOL-03",
        "name": "हर्कबहादुर पुन",
        "name_en": "Harka Bahadur Pun",
        "org": "सशस्त्र प्रहरी विपद् उद्धार",
        "phone": "9848334455",
        "equipment": "४x४ उद्धार भ्यान",
        "equipment_en": "4x4 Emergency High-Axle Van"
    },
    {
        "rescuer_id": "VOL-04",
        "name": "अनिल थारु",
        "name_en": "Anil Tharu",
        "org": "राप्ती सोनारी युवा स्वयंसेवक",
        "phone": "9848445566",
        "equipment": "ट्र्याक्टर र उद्धार डोरी",
        "equipment_en": "High-Axle Tractor & Ropes"
    }
]

class EvacuationTriageEngine:
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
                (h.get("elderly", 0) * 1.8) +
                (h.get("children", 0) * 1.3) +
                (h.get("disabled", 0) * 3.0) +
                (h.get("pregnant", 0) * 2.5) +
                (4.0 if h.get("medical_dependency") else 0.0) +
                (h.get("residents", 1) * 0.3)
            )

            hazard_index = depth * 3.8
            time_urgency = max(1.0, 5.0 - (lead_time_hrs if lead_time_hrs is not None else 3.0))

            if depth > 0:
                epi = round((hazard_index * b_fragility) + (vuln_score * 1.8) + time_urgency, 2)
            else:
                epi = round(vuln_score * 0.1, 2)

            if epi >= 20.0 or h.get("structural_collapse_threat"):
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

        # Allocate dedicated volunteer rescue team to top priority cases
        for idx, h in enumerate(ranked):
            if h["priority_level"] in ["IMMEDIATE_EVACUATION", "HIGH_PRIORITY"]:
                rescuer = VOLUNTEER_UNITS[idx % len(VOLUNTEER_UNITS)]
                h["assigned_rescuer"] = rescuer
            else:
                h["assigned_rescuer"] = None

        return ranked
