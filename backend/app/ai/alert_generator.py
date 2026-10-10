import requests
from typing import Dict, Any, Optional

class OllamaAlertGenerator:
    OLLAMA_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "phi3:latest"

    @classmethod
    def generate_llm_alert(
        cls,
        household: Dict[str, Any],
        forecast: Dict[str, Any],
        model: str = DEFAULT_MODEL,
        language: str = "ne"
    ) -> Dict[str, Any]:
        hh_id = household["household_id"]
        name = household.get("head_of_household", "नागरिक")
        vuln_person = household.get("vulnerability_details", "परिवार")
        depth = household.get("predicted_water_depth_m", 0.0)
        shelter = household.get("nearest_shelter", "श्री सरस्वती माध्यमिक विद्यालय")
        rescuer = household.get("assigned_rescuer") or {
            "name": "सागर थापा",
            "name_en": "Sagar Thapa",
            "phone": "9848112233",
            "equipment": "उद्धार बोट",
            "equipment_en": "Rescue Boat"
        }

        r_name = rescuer["name"] if language == "ne" else rescuer["name_en"]
        r_phone = rescuer["phone"]
        r_equip = rescuer["equipment"] if language == "ne" else rescuer["equipment_en"]

        if language == "en":
            fallback = (
                f"URGENT [{hh_id}]: {name}, flood will reach {depth}m! "
                f"Rescuer {r_name} ({r_phone}) is dispatched with {r_equip} to evacuate your family ({vuln_person}). "
                f"Prepare to move to {shelter} immediately."
            )
        else:
            fallback = (
                f"खतरा [{hh_id}]: {name} जी, घरमा बाढी {depth}m पुग्दैछ! "
                f"उद्धारकर्ता {r_name} ({r_phone}) {r_equip} सहित तपाईंलाई लिन आउँदै हुनुहुन्छ। "
                f"{vuln_person} सहित तुरुन्तै {shelter} जान तयार हुनुहोस्।"
            )

        # Attempt Ollama Phi-3 personalized refinement
        prompt = (
            f"Write an urgent 25-word emergency evacuation SMS.\n"
            f"Resident: {name}\n"
            f"Flood Depth: {depth}m\n"
            f"Vulnerable member: {vuln_person}\n"
            f"Designated Shelter: {shelter}\n"
            f"Rescuer coming to save them: {r_name} (Phone: {r_phone}, {r_equip})\n"
            f"Language: {'Nepali' if language == 'ne' else 'English'}\n"
            f"SMS:"
        )

        try:
            resp = requests.post(
                cls.OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 70}
                },
                timeout=5.0
            )
            if resp.status_code == 200:
                text = resp.json().get("response", "").strip().strip('"\n ')
                if r_name in text or r_phone in text:
                    return {"alert_text": text, "engine": f"ollama-{model}", "is_llm": True}
        except Exception:
            pass

        return {"alert_text": fallback, "engine": "grounded-edge-engine", "is_llm": False}
