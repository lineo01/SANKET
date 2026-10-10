# 🌊 Nepal Flood Watch — AI-Based Live Flood Risk Prediction

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Machine Learning](https://img.shields.io/badge/Model-XGBoost-orange)
![Data](https://img.shields.io/badge/Data-Live%20%2B%20Historical-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)

**Nepal Flood Watch** is an AI-powered flood early-warning system designed to monitor river conditions across Nepal and predict future flood risk.

It combines:

- Live river water-level observations from Nepal’s Department of Hydrology and Meteorology (DHM)
- Live and forecast rainfall data
- Satellite-based precipitation data
- Simulated river-discharge forecasts from GloFAS
- Terrain and catchment features
- Historical flood-event records

The system uses **XGBoost** to predict:

1. Future river water level  
2. Future river discharge  
3. Flood risk status: `Normal`, `Watch`, `Warning`, `Danger`, or `Extreme`

---

## 🚨 Why This Project Matters

Nepal experiences severe monsoon flooding every year, especially in river basins such as the Koshi, Gandaki, Karnali, Bagmati, and Rapti. Floods can develop rapidly after intense rainfall in upstream mountain areas, often before communities downstream realize the danger.

Existing monitoring systems provide valuable observations, but this project aims to make that information more actionable by combining multiple data sources into a single machine-learning-based early-warning platform.

**Goal:**  
Give communities, local governments, and disaster-response teams an early and understandable flood-risk signal.

---

## 🎯 Project Objectives

- Collect live hydrological and meteorological data for Nepal
- Build a clean, time-series flood dataset
- Predict future river water level using XGBoost
- Estimate flood-flow intensity using discharge and terrain features
- Classify flood risk into clear warning levels
- Display live risk status on an interactive map
- Provide a scalable foundation for a national flood-warning system

---

## 🧠 How the System Works

```text
Live Data Sources
        │
        ▼
┌─────────────────────────────┐
│  DHM River Water Level      │
│  Open-Meteo Rainfall        │
│  Open-Meteo Flood API       │
│  NASA GPM IMERG             │
│  DEM / Terrain Data         │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│   Feature Engineering       │
│   - Rolling rainfall        │
│   - Water-level change      │
│   - Discharge change        │
│   - Soil moisture           │
│   - Forecast rainfall       │
│   - Terrain features        │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│        XGBoost Models       │
│  - Water-level prediction   │
│  - Discharge prediction     │
│  - Flood-risk classifier    │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  Live Dashboard / Alerts    │
│  - Station map              │
│  - Risk color coding        │
│  - Forecast charts          │
│  - Warning notifications    │
└─────────────────────────────┘
```

---

## 📡 Live Data Sources

| Data | Source | Purpose |
|---|---|---|
| River water level | [DHM River Watch](https://dhm.gov.np/hydrology/river-watch) | Real-time observed water level, warning level, danger level, and trend |
| Real-time stream flow | [DHM Real-Time Stream Flow](https://dhm.gov.np/hydrology/realtime-stream) | Station-wise water level and discharge where available |
| Rainfall forecast | [Open-Meteo Weather API](https://open-meteo.com/en/docs) | Hourly past and forecast rainfall |
| River discharge forecast | [Open-Meteo Flood API](https://open-meteo.com/en/docs/flood-api) | GloFAS-based daily river discharge and ensemble forecast |
| Satellite rainfall | [NASA GPM IMERG](https://gpm.nasa.gov/data/imerg) | Basin-wide precipitation, especially in areas with few ground stations |
| Historical flood events | [DesInventar Nepal](https://www.desinventar.net/DesInventar/main.jsp?countrycode=npl&lang=EN) | Historical flood impact records for training labels |
| Disaster records | BIPAD / NDRRMA | Recent flood damage and incident records |
| Terrain data | Copernicus DEM / SRTM | Elevation, slope, drainage area, and catchment characteristics |
| Flood extent | Sentinel-1 SAR / Sentinel-2 | Satellite-based mapping of areas actually flooded |

---

## 🤖 Machine Learning Approach

The project uses separate models instead of forcing one model to predict everything.

### 1. Water-Level Prediction

**Model:** `XGBRegressor`

Predicts river water level for:

- Next 1 hour
- Next 3 hours
- Next 6 hours
- Next 12 hours
- Next 24 hours

**Main input features:**

- Current water level
- Water-level change over 1, 3, 6, 12, and 24 hours
- Current and previous discharge
- Rainfall over the last 3, 6, 12, 24, 48, and 72 hours
- Forecast rainfall for the next 6, 12, 24, and 48 hours
- Upstream catchment rainfall
- Soil moisture
- Month and monsoon indicator
- Station and basin information

### 2. Discharge / Flow-Intensity Prediction

**Model:** `XGBRegressor`

Predicts future river discharge in cubic metres per second.

Discharge is important because it represents the volume of water moving through a river. A rapid increase in discharge can indicate an approaching flood even before the downstream water level rises sharply.

**Input features include:**

- Current GloFAS discharge
- Discharge change over time
- Forecast discharge
- Ensemble maximum discharge
- Upstream rainfall
- Catchment area
- Slope and elevation

### 3. Flood-Risk Classification

**Model:** `XGBClassifier`

Classifies each station into one of five risk levels:

| Risk Level | Meaning |
|---|---|
| `Normal` | Water level is below warning threshold |
| `Watch` | Water level is rising or approaching warning level |
| `Warning` | Water level has reached or exceeded warning level |
| `Danger` | Water level has reached or exceeded danger level |
| `Extreme` | Severe exceedance, high forecast discharge, or major flood likelihood |

Initial labels are created using DHM’s published warning and danger thresholds. These labels can later be improved using historical flood events and satellite-derived flood maps.

---

## 📊 Example Model Input

| Feature | Example Value |
|---|---:|
| Station | Bagmati River Station |
| Current water level | 4.82 m |
| Warning level | 5.20 m |
| Danger level | 5.80 m |
| Water-level change, 6 h | +0.34 m |
| Rainfall, last 24 h | 86.4 mm |
| Forecast rainfall, next 24 h | 54.2 mm |
| Soil moisture, 3–9 cm | 0.34 m³/m³ |
| River discharge | 1,240 m³/s |
| Forecast discharge, next day | 1,610 m³/s |
| Ensemble maximum discharge | 1,740 m³/s |
| Predicted risk | `Warning` |

---

## 🗂️ Project Structure

```text
nepal-flood-watch/
│
├── data/
│   ├── raw/                  # Raw API responses and scraped data
│   ├── processed/            # Cleaned model-ready datasets
│   └── external/             # DEM, basin boundaries, historical records
│
├── src/
│   ├── data_collection/
│   │   ├── dhm_scraper.py
│   │   ├── open_meteo_weather.py
│   │   ├── open_meteo_flood.py
│   │   └── imerg_downloader.py
│   │
│   ├── preprocessing/
│   │   ├── clean_data.py
│   │   ├── feature_engineering.py
│   │   └── create_labels.py
│   │
│   ├── models/
│   │   ├── train_water_level.py
│   │   ├── train_discharge.py
│   │   ├── train_risk_classifier.py
│   │   └── evaluate_models.py
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   └── map_components.py
│   │
│   └── utils/
│       ├── config.py
│       └── helpers.py
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_model_evaluation.ipynb
│
├── models/
│   ├── water_level_model.json
│   ├── discharge_model.json
│   └── risk_classifier.json
│
├── requirements.txt
├── LICENSE
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone [https://github.com/your-username/nepal-flood-watch.git](https://github.com/your-username/nepal-flood-watch.git)
cd nepal-flood-watch
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Required Python packages

```text
pandas
numpy
requests
beautifulsoup4
lxml
scikit-learn
xgboost
matplotlib
seaborn
folium
streamlit
joblib
python-dateutil
```

---

## 🚀 Quick Start

### Fetch live weather data

```python
import requests

lat = 27.7172
lon = 85.3240

url = (
    "[https://api.open-meteo.com/v1/forecast](https://api.open-meteo.com/v1/forecast)"
    f"?latitude={lat}&longitude={lon}"
    "&hourly=temperature_2m,precipitation,rain,soil_moisture_3_to_9cm"
    "&past_days=7&forecast_days=7&timezone=Asia%2FKathmandu"
)

response = requests.get(url)
data = response.json()

print(data["hourly"].keys())
```

### Fetch river-discharge forecast

```python
import requests

lat = 26.8
lon = 87.0

url = (
    "[https://flood-api.open-meteo.com/v1/flood](https://flood-api.open-meteo.com/v1/flood)"
    f"?latitude={lat}&longitude={lon}"
    "&daily=river_discharge,river_discharge_mean,"
    "river_discharge_max,river_discharge_min"
    "&past_days=30&forecast_days=30"
)

response = requests.get(url)
data = response.json()

print(data["daily"].keys())
```

### Train the flood-risk model

```bash
python src/models/train_risk_classifier.py
```

### Run the dashboard

```bash
streamlit run src/dashboard/app.py
```

---

## 📈 Model Evaluation

The models are evaluated using:

| Task | Metrics |
|---|---|
| Water-level prediction | MAE, RMSE, R² |
| Discharge prediction | MAE, RMSE, R² |
| Risk classification | Accuracy, Precision, Recall, F1-score, Confusion Matrix |

For flood-warning systems, **recall for `Warning`, `Danger`, and `Extreme` classes is especially important**. A system that misses a dangerous flood is more harmful than one that occasionally gives a cautious early warning.

---

## 🗺️ Planned Dashboard Features

- Interactive map of DHM river stations
- Color-coded live flood-risk status
- 6-hour, 12-hour, and 24-hour forecast view
- Rainfall and discharge charts
- Station-level warning and danger thresholds
- Upstream rainfall visualization
- Alerts for rapidly rising rivers
- Historical flood-event overlay
- Mobile-friendly warning interface

---

## ⚠️ Limitations

- GloFAS and Open-Meteo discharge values are **model simulations**, not direct sensor measurements.
- DHM data may not be available for every river or district.
- XGBoost can predict river-level risk well, but it cannot fully replace a physical hydraulic model for estimating exact flood depth and spread.
- Flood velocity over land requires additional hydraulic modeling, such as HEC-RAS 2D, or calibration using field data.
- Satellite flood mapping depends on satellite revisit time and weather conditions.

---

## 🔭 Future Improvements

- Add Sentinel-1 SAR-based flood-extent detection
- Integrate HEC-RAS 2D for flood depth and inundation mapping
- Add landslide and glacial lake outburst flood (GLOF) indicators
- Use LSTM or Transformer models for longer time-series forecasting
- Add SMS and community alert integration
- Build offline-capable mobile alerts for rural areas
- Expand coverage to all major Nepali river basins
- Collaborate with DHM, ICIMOD, and local disaster-management authorities

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository  
2. Create a new branch: `git checkout -b feature-name`  
3. Commit your changes: `git commit -m "Add feature"`  
4. Push to the branch: `git push origin feature-name`  
5. Open a pull request  

---

## 👥 Team

**LINEO**  
Project Developer / Machine Learning & Systems Design  
Kathmandu, Nepal

---

## 📜 License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Nepal Department of Hydrology and Meteorology (DHM)
- Open-Meteo
- Copernicus Climate Change Service / GloFAS
- NASA Global Precipitation Measurement Mission
- European Space Agency Copernicus Programme
- DesInventar and BIPAD disaster databases
- ICIMOD and the open-source geospatial community
