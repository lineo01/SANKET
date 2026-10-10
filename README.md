# 🌊 Nepal Flood Watch

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![ML](https://img.shields.io/badge/ML-XGBoost-orange)
![Status](https://img.shields.io/badge/Status-Early%20Prototype-yellow)

**Nepal Flood Watch** is an early-stage flood-monitoring and risk-analysis platform for Nepal. It is designed to combine live river observations, rainfall forecasts, modeled river discharge, and terrain information to help users understand current and near-future flood risk.

This repository is a **working prototype**, not an operational emergency-warning system. Its current focus is on building a reliable data pipeline, API, frontend, and an experimentally validated XGBoost flood-risk model.

---

## ⚠️ What Is Implemented vs Planned

This project intentionally separates what is working from what is planned.

| Area | Status | Details |
|---|---|---|
| FastAPI backend | ✅ Implemented | Modular backend with API, services, data, AI, and configuration layers |
| React frontend | ✅ Implemented | Frontend application structure with reusable components and TypeScript types |
| Flood alert node | 🚧 In progress | `alert-server/flood_node` is intended to handle local alerting and device/server communication |
| Open-Meteo rainfall API | ✅ Implemented / testable | Retrieves hourly rainfall, temperature, and soil-moisture data |
| Open-Meteo Flood API | ✅ Implemented / testable | Retrieves GloFAS-based river-discharge history and forecasts |
| DHM live river data | 🚧 In progress | DHM River Watch is the intended source for observed water level and official thresholds |
| XGBoost risk model | 🧪 Experimental | Model design and training pipeline are under development; results depend on availability of a sufficiently long historical dataset |
| Sentinel-1 flood mapping | 🗺️ Roadmap | Not yet part of the active pipeline |
| NASA IMERG basin rainfall | 🗺️ Roadmap | Planned for upstream catchment rainfall estimation |
| DEM-based catchment delineation | 🗺️ Roadmap | Planned using tools such as PyShed, WhiteboxTools, or RichDEM |
| Hydraulic flood-depth modeling | 🗺️ Roadmap | HEC-RAS 2D or similar model would be required for actual inundation depth and spread |

> **Important:** This project does not yet claim to predict exact flood depth, flood velocity over land, or the precise area that will be inundated. Those outputs require calibrated hydraulic modeling and validated historical observations.

---

## 🎯 Problem Statement

During Nepal’s monsoon season, intense rainfall in upstream mountain and hill areas can cause river levels to rise rapidly downstream. Communities near rivers may have limited time to respond, especially when rainfall occurs far from the affected location.

The goal of this project is to build a transparent decision-support tool that:

- Monitors rainfall and river-related indicators
- Combines observed and forecast data
- Highlights stations or areas with elevated flood risk
- Provides a foundation for future early-warning services

It is designed as a **decision-support prototype**, not a replacement for official warnings from Nepal’s Department of Hydrology and Meteorology (DHM), National Disaster Risk Reduction and Management Authority (NDRRMA), or local authorities.

---

## 🧠 System Overview

```text
┌────────────────────────────────────────────┐
│              External Data Sources          │
│                                            │
│  DHM River Watch       Open-Meteo Weather  │
│  Open-Meteo Flood API  NASA IMERG (planned)│
│  DEM / HydroSHEDS      Sentinel-1 (planned)│
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│                Backend / FastAPI            │
│                                            │
│  data collection → validation → storage    │
│  feature engineering → ML inference        │
│  risk rules → REST API                     │
└───────────────────┬────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐   ┌────────────────────┐
│  React Frontend  │   │  Alert Server /     │
│  Dashboard / UI  │   │  Flood Node         │
└──────────────────┘   └────────────────────┘
```

---

## 📡 Data Sources

### Currently used or being integrated

| Data | Source | Use in Project |
|---|---|---|
| Hourly rainfall, temperature, soil moisture | [Open-Meteo Weather API](https://open-meteo.com/en/docs) | Current and forecast weather features |
| River discharge history and forecast | [Open-Meteo Flood API](https://open-meteo.com/en/docs/flood-api) | GloFAS-based discharge features |
| River water level, warning and danger thresholds | [DHM River Watch](https://dhm.gov.np/hydrology/river-watch) | Intended primary observed river-level source |

### Planned data sources

| Data | Source | Planned Use |
|---|---|---|
| Basin-wide satellite rainfall | [NASA GPM IMERG](https://gpm.nasa.gov/data/imerg) | Estimate rainfall over upstream catchments |
| Flood-extent labels | Sentinel-1 SAR / Sentinel-2 | Validate whether flooding occurred |
| Elevation, slope, drainage area | Copernicus DEM / SRTM / HydroSHEDS | Terrain and catchment features |
| Historical flood impacts | DesInventar Nepal, BIPAD / NDRRMA | Create historical flood-event labels |

---

## 🤖 Machine Learning Approach

The project plans to use XGBoost for tabular flood-risk prediction. XGBoost is suitable for structured time-series features such as rainfall totals, water-level changes, discharge changes, soil moisture, and terrain attributes.

### Prediction targets

| Target | Model Type | Status |
|---|---|---|
| Future water level | XGBoost Regressor | Experimental |
| Future discharge / flow indicator | XGBoost Regressor | Experimental |
| Flood-risk class | XGBoost Classifier | Experimental |

### Proposed risk classes

| Class | Meaning |
|---|---|
| `normal` | No immediate concern |
| `watch` | Rising trend or approaching warning threshold |
| `warning` | Warning threshold reached or high forecast risk |
| `danger` | Danger threshold reached or severe forecast risk |
| `extreme` | Major exceedance or high-confidence extreme event signal |

### Important modeling note

The system will not train an XGBoost model to “predict GloFAS discharge using GloFAS discharge” as its main objective. GloFAS discharge is treated as an **external hydrological feature**, while the primary supervised targets are:

1. Observed DHM water level, where historical observations are available  
2. A risk label derived from DHM thresholds and validated historical flood events  

If observed DHM history is unavailable for a pilot basin, the project will clearly state that the model is being developed using proxy data or scenario-based evaluation—not claim operational accuracy.

---

## 📊 Feature Engineering

Planned features include:

- Current water level
- Water-level change over 1, 3, 6, 12, and 24 hours
- Current and lagged discharge
- Discharge change over time
- Rainfall over 1, 3, 6, 12, 24, 48, and 72 hours
- Forecast rainfall for 6, 12, 24, and 48 hours
- Upstream catchment rainfall
- Soil moisture at multiple depths
- Month, hour, and monsoon-season indicator
- Basin and station metadata
- Elevation, slope, drainage area, and distance to river

Rainfall will be aggregated over the upstream catchment rather than using only the rainfall at the gauge location.

---

## 🧪 Model Validation

To avoid misleading results, the project will use time-aware validation.

- Train on earlier periods
- Validate on later periods
- Use `TimeSeriesSplit` or event-based temporal splits
- Avoid random row-wise splitting, which can leak future information into training
- Evaluate separately for each forecast horizon
- Report recall, precision, F1-score, and confusion matrix for warning-level classes

For flood-warning systems, recall on `warning`, `danger`, and `extreme` classes is more important than overall accuracy. A model that misses a dangerous event is more harmful than one that occasionally gives a cautious early warning.

---

## 🗂️ Repository Structure

```text
.
├── alert-server/
│   └── flood_node/              # Local alerting / flood-node service
│
├── backend/
│   ├── app/
│   │   ├── ai/                  # ML inference and model utilities
│   │   ├── api/                 # FastAPI routes
│   │   ├── core/                # Configuration and core settings
│   │   ├── data/                # Data-access and database logic
│   │   ├── models/              # Pydantic / database models
│   │   └── services/            # Business logic and external data services
│   ├── tests/                   # Backend tests
│   └── venv/                    # Local virtual environment, not committed
│
├── data/                        # Raw, processed, and external datasets
├── docs/                        # Project documentation and diagrams
├── flood-detect/                # Flood-detection experiments / components
├── frontend/
│   └── src/
│       ├── components/          # Reusable React components
│       └── types/               # TypeScript type definitions
│
├── .env.example
├── requirements.txt
└── README.md
```

> The `backend/venv/` folder should not be committed to Git. Add it to `.gitignore`.

---

## ⚙️ Backend Setup

### 1. Clone the repository

```bash
git clone [https://github.com/your-username/nepal-flood-watch.git](https://github.com/your-username/nepal-flood-watch.git)
cd nepal-flood-watch
```

### 2. Create and activate a virtual environment

```bash
cd backend
python -m venv venv

# Windows PowerShell
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Example variables:

```env
APP_ENV=development
DATABASE_URL=sqlite:///./flood_watch.db
OPEN_METEO_BASE_URL=[https://api.open-meteo.com/v1](https://api.open-meteo.com/v1)
OPEN_METEO_FLOOD_BASE_URL=[https://flood-api.open-meteo.com/v1](https://flood-api.open-meteo.com/v1)
DHM_RIVER_WATCH_URL=[https://dhm.gov.np/hydrology/river-watch](https://dhm.gov.np/hydrology/river-watch)
```

### 5. Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

## 🌐 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Then open the local development URL shown by Vite, usually:

```text
http://localhost:5173
```

---

## 🚀 Example API Usage

### Get weather and rainfall data

```text
GET /api/weather?latitude=27.7172&longitude=85.3240
```

Example backend request to Open-Meteo:

```text
[https://api.open-meteo.com/v1/forecast?latitude=27.7172&longitude=85.3240](https://api.open-meteo.com/v1/forecast?latitude=27.7172&longitude=85.3240)
&hourly=temperature_2m,precipitation,rain,soil_moisture_3_to_9cm
&past_days=7&forecast_days=7&timezone=Asia%2FKathmandu
```

### Get river-discharge forecast

```text
GET /api/flood/discharge?latitude=26.8&longitude=87.0
```

Example backend request to Open-Meteo Flood API:

```text
[https://flood-api.open-meteo.com/v1/flood?latitude=26.8&longitude=87.0](https://flood-api.open-meteo.com/v1/flood?latitude=26.8&longitude=87.0)
&daily=river_discharge,river_discharge_mean,river_discharge_max,river_discharge_min
&past_days=30&forecast_days=30
```

The Flood API returns daily simulated river discharge in m³/s, including ensemble mean, maximum, and minimum values where requested.

---

## 🧪 Running Tests

From the `backend/` directory:

```bash
pytest
```

Tests currently focus on backend correctness, API behavior, and data-service logic. Model evaluation notebooks and reports will be added as the ML pipeline matures.

---

## 📈 Current Development Focus

1. Build a stable DHM ingestion and storage workflow  
2. Create a clean station-time-series dataset  
3. Add upstream rainfall aggregation  
4. Implement temporal train/test splitting  
5. Train and evaluate an initial XGBoost risk classifier  
6. Publish honest evaluation metrics and known fai# 🌊 Nepal Flood Watch — AI-Based Live Flood Risk Prediction

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
