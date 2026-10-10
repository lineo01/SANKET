import joblib
import pandas as pd

bundle = joblib.load("sanket_model.joblib")
model = bundle["model"]
features = bundle["features"]


def predict_risk(
    water_level_m,
    rainfall_mm_15m,
    rainfall_mm_60m,
    level_change_5m,
    level_change_15m,
    upstream_level_m,
):
    readings = pd.DataFrame(
        [
            {
                "water_level_m": water_level_m,
                "rainfall_mm_15m": rainfall_mm_15m,
                "rainfall_mm_60m": rainfall_mm_60m,
                "level_change_5m": level_change_5m,
                "level_change_15m": level_change_15m,
                "upstream_level_m": upstream_level_m,
            }
        ]
    )

    risk = float(model.predict_proba(readings[features])[0, 1])

    if risk >= 0.70:
        status = "HIGH SIMULATED RISK"
    elif risk >= 0.40:
        status = "ELEVATED SIMULATED RISK"
    else:
        status = "LOW SIMULATED RISK"

    return {"risk": risk, "status": status}


if __name__ == "__main__":
    result = predict_risk(
        water_level_m=3.3,
        rainfall_mm_15m=18.0,
        rainfall_mm_60m=45.0,
        level_change_5m=0.12,
        level_change_15m=0.30,
        upstream_level_m=3.5,
    )

    print(f"Predicted probability: {result['risk']:.1%}")
    print(f"Status: {result['status']}")
