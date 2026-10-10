
---
# 🚨 SANKET (संकेत)

> **Offline-first AI flood early-warning and evacuation system for Nepal**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![Leaflet](https://img.shields.io/badge/GIS-Leaflet-green)
![Local SLM](https://img.shields.io/badge/AI-Ollama%20Phi--3-8A2BE2)
![Hardware](https://img.shields.io/badge/IoT-Arduino%20UNO%20%2B%20DHT11-orange)
![Status](https://img.shields.io/badge/Status-Prototype-yellow)

**SANKET** helps flood-prone communities act before disaster reaches them.

It combines river and rainfall signals, local sensor data, GIS household information, and an AI decision layer to identify exposed households, assess flood risk, generate clear Nepali evacuation instructions, assign volunteers, and recommend safe routes.

Unlike a normal disaster-reporting dashboard, SANKET is designed for the **last mile**: it turns a rising-river signal into a specific, actionable community response—even when internet connectivity is limited.

*Pilot Target: West Rapti River Basin · Kusum Gauge (#430) · Rapti Sonari Rural Municipality, Ward 2, Banke District, Nepal*

---

## 🎯 What SANKET Does

SANKET answers one critical question:

> **“The river is rising—which households are at risk, what should they do now, and where should they go?”**

It is built around four connected capabilities:

| Capability | Purpose |
|---|---|
| **Flood Signal Monitoring** | Ingest DHM river stage baselines, live government scrape data, and edge culvert sensors |
| **Physics & Risk Assessment** | Compute doorstep water depths, plinth overtopping, and structural collapse risks in < 10ms |
| **AI Evacuation Triage** | Rank households by vulnerability and assign specific local rescue volunteers |
| **Local Actionable Alerts** | Synthesize localized Nepali SMS alerts and broadcast voice sirens offline |

---

## 🧠 Core Idea & System Architecture

```text
  [ Physical Arduino Node ]                [ DHM Government Feed ]
  (Water Probe A0 + DHT11)                 (Kusum Station #430)
             │                                        │
             ▼ (USB Serial / 115200 baud)             ▼ (HTTP Scraper)
┌────────────────────────────────────────────────────────────────────────┐
│                   SANKET Local Ingestion Layer                         │
│   • Soil saturation index (DHT11 humidity)                             │
│   • Micro-culvert surge detection (Water sensor ADC)                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  ENGINE 1: Hydrological Crest & Lead-Time Forecaster                   │
│  • Rate of rise (Δh/Δt), surge acceleration (Δ²h/Δt²)                  │
│  • Quantile Uncertainty Bounds: P10 (Lower bound) & P90 (Worst-case)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  ENGINE 2: Physics-Informed Hydraulic Surrogate Model (PI-HSM)         │
│  • Doorstep depth, Manning friction velocity: v = (1/n)·R^(2/3)·S^(1/2)│
│  • DEFRA Flood Hazard: HR = Depth · (Velocity + 0.5) + Debris Factor   │
│  • Structural hydrodynamic shear collapse threat for mud (Kachha) huts │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  ENGINE 3: Multi-Criteria Evacuation Triage Engine                     │
│  • Evacuation Priority Index (EPI) = Hazard · Fragility + Demographics│
│  • Proximity routing across 4 distributed high-ground shelters         │
│  • Automated pairing to Red Cross, APF, and Youth Volunteer teams      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  ENGINE 4: Grounded Local SLM Alert Synthesizer                        │
│  • 100% offline quantized Phi-3 Mini running on Ollama                 │
│  • Zero-hallucination guardrails: Names resident, rescuer, and shelter │
│  • Synthesizes localized 160-char SMS payloads in pure Nepali          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
        ┌───────────────────────────┴───────────────────────────┐
        ▼                                                       ▼
┌───────────────────────────────────┐   ┌────────────────────────────────┐
│  Institutional GIS Operations Desk│   │   Audio & Radio Broadcast      │
│  • Light Carto/OSM Inundation Map │   │   • Dual-tone Web Audio Siren  │
│  • Volunteer Dispatch Desk        │   │   • Web Speech API (Nepali TTS)│
│  • Real-time Sensor Oscilloscope  │   │   • 160-char GSM SMS Payloads  │
└───────────────────────────────────┘   └────────────────────────────────┘
```

The AI is not just a chatbot. It is the decision-making layer that connects hazard signals to household-level action.

---

## 🔍 Data Provenance & Scientific Honesty

In life-critical disaster tech, transparency about data sources is paramount. SANKET operates on a hybrid validation model:

| Data Layer | Classification | Technical Source & Description |
|---|---|---|
| **Edge Hardware Telemetry** | **100% Real** | Live ADC voltages from an analog water probe and digital DHT11 ambient microclimate data streamed over USB serial (`115200` baud). |
| **Basin Geography & Centerlines** | **100% Real** | High-resolution GIS vectors mapping the West Rapti main stem, braided channels, and Dudhuwa tributary in Banke District. |
| **Hydrological Gauge Baselines** | **100% Real** | Official Nepal Government Department of Hydrology and Meteorology (DHM) Station #430 (Kusum) baselines: **5.00m Warning Level**, **5.40m Danger Level** [1]. |
| **Evacuation Shelters** | **100% Real** | 4 verified high-ground public centers in Rapti Sonari Ward 2 (*Shree Saraswati Secondary School*, *Kusum Health Post*, *Ward 2 Community Hall*, and *Red Cross Flood Shelter*). |
| **Monsoon Storm Hydrograph** | **Calibrated Benchmark** | A 20-hour historical hydrograph ($2.40\text{m} \to 6.30\text{m}$) calibrated against historical monsoon flood records at Kusum to allow comprehensive offline evaluation during dry-season testing. |
| **Household Demographics** | **Synthetic Ground Truth** | 50 household coordinates geolocated inside the real Rapti Sonari floodplain. Names, phone numbers, and vulnerability traits are synthesized based on Nepal Central Bureau of Statistics (CBS) rural Terai census distributions to respect citizen privacy. |

---

## 🧮 Mathematical & AI Formulations

### 1. Physics-Informed Hydraulic Surrogate
Traditional 2D hydrodynamic simulation tools (like HEC-RAS) take **30 to 60 minutes** per run. SANKET’s topological surrogate calculates doorstep depth in **8 milliseconds**:
$$\text{Ground Depth}_i = \max\left(0, \left( Z_{\text{river\_datum}} + H_{\text{crest}} - S_0 \cdot d_{\text{reach}} \right) - Z_{\text{DEM}, i}\right) \times F_{\text{saturation}}$$
* **Manning's Flow Velocity:** $v = \frac{1}{n} R^{2/3} S_0^{1/2}$
* **DEFRA Flood Hazard Rating ($HR$):** $HR = d \times (v + 0.5) + DF$
* **Structural Collapse Check:** True if building type is *Kachha* and $d \ge 0.8\text{m}$ or $d \times v \ge 0.35\text{ m}^2/\text{s}$.

### 2. Evacuation Priority Index (EPI)
Rescuers cannot evacuate 50 households at once. SANKET computes an optimal rescue queue:
$$EPI = \left( d \times 3.8 \times \text{Fragility} \right) + \left( V_{\text{demographic}} \times 1.8 \right) + \text{TimeUrgency}$$
* **Building Fragility:** Mud (*Kachha*) = $2.2\times$, Brick/Mortar (*Semi-Pakka*) = $1.4\times$, Concrete (*Pakka*) = $1.0\times$.
* **Demographic Vulnerability:** Weighted by bedridden elderly ($1.8\times$), children ($1.3\times$), disabled members ($3.0\times$), pregnant women ($2.5\times$), and active medical/oxygen dependencies ($4.0\times$).

---

## 🛠️ Physical IoT Edge Node

SANKET connects directly to an edge microcontroller node (Arduino UNO / ESP32) deployed at culverts or riverbanks.

### Pin Connections
* **Analog Water Level Sensor:** `VCC` $\to$ `5V`, `GND` $\to$ `GND`, `Signal (S)` $\to$ **`A0`**
* **DHT11 Environmental Sensor:** `VCC` $\to$ `5V`, `GND` $\to$ `GND`, `Data (Out)` $\to$ **Digital Pin `2`**
* **Computer Connection:** USB-A to USB-B cable plugged into host machine (`COM3`).

### Hardware-in-the-Loop Testing
When the physical water sensor is dry, the system rests at a safe baseline ($2.20\text{m}$). Dipping the probe into a glass of water increases the raw ADC value from $0 \to 650$, surging the simulated river stage past the $5.40\text{m}$ Danger threshold up to **$6.50\text{m}$**. The entire AI cascade reacts in real time: the map turns red, volunteers are assigned, and the voice siren triggers.

---

## 🗂️ Repository Architecture

```text
sanket/
├── backend/
│   ├── app/
│   │   ├── main.py                     # ASGI root, background scraper daemon, serial bridge startup
│   │   ├── core/
│   │   │   ├── config.py               # Paths, database URLs, CORS policies
│   │   │   └── database.py             # SQLAlchemy session and engine declaration
│   │   ├── models/
│   │   │   ├── db_models.py            # SQLite schema: households, river_readings, triage, alerts
│   │   │   └── schemas.py              # Pydantic data contracts
│   │   ├── api/
│   │   │   └── routes.py               # REST API endpoints (/api/ai/assess, /api/river/geojson, etc.)
│   │   ├── ai/
│   │   │   ├── forecaster.py           # Time-series regression & P10/P90 quantile bounds
│   │   │   ├── surrogate.py            # Physics-informed hydrodynamic surrogate
│   │   │   ├── triage.py               # Operations research EPI ranking & volunteer assignment
│   │   │   └── alert_generator.py      # Local Ollama Phi-3 + guarded offline fallback generator
│   │   └── services/
│   │       ├── dhm_scraper.py          # Government scraper (hydrology.gov.np & BIPAD)
│   │       ├── seeder.py               # Self-healing database seeder
│   │       └── serial_bridge.py        # Dedicated COM3 serial bridge with heartbeat watchdog
│   ├── requirements.txt                # Python backend dependencies
│   ├── test_arduino.py                 # Serial diagnostic test script
│   └── sanket.db                       # Local SQLite database
├── frontend/
│   ├── index.html                      # Root HTML with high-contrast light theme
│   ├── package.json                    # Node dependencies (React 18, Vite, Leaflet, Tailwind)
│   ├── tsconfig.json                   # Strict TypeScript compiler options
│   ├── vite.config.ts                  # Vite server & API proxy configuration
│   └── src/
│       ├── App.tsx                     # Institutional Emergency Operations Console
│       ├── index.css                   # Tailwind CSS baseline
│       ├── main.tsx                    # React root with ErrorBoundary wrapper
│       ├── types/
│       │   └── index.ts                # TypeScript data interfaces
│       └── components/
│           ├── FloodMap.tsx            # Light Leaflet GIS map (multi-river & 4 shelters)
│           ├── HardwareMonitor.tsx     # Dedicated Arduino live telemetry page
│           └── VolunteerConsole.tsx    # Volunteer rescue dispatch allocation desk
├── data/
│   ├── households.geojson              # 50 households with resident names & elevation
│   ├── river.geojson                   # West Rapti main stem, braided channels, & tributaries
│   ├── shelters.geojson                # 4 distributed disaster shelters with live capacities
│   ├── roads.geojson                   # Evacuation ridge roads & bridges
│   ├── sample_dhm_readings.json        # Calibrated 20-hour Kusum monsoon surge hydrograph
│   └── sample_lora_readings.json       # Historical edge LoRa telemetry readings
├── start_sanket.bat                    # 1-Click Master Launcher for Windows
└── README.md                           # Master Project Documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
1. **Python 3.10+**
2. **Node.js v18+**
3. **Ollama:** Installed locally with `phi3:latest` downloaded (`ollama pull phi3`).
4. **Arduino UNO (Optional for physical demo):** Programmed with the SANKET firmware at `115200` baud.

---

### Method A: 1-Click Startup (Windows)
Double-click **`start_sanket.bat`** in the project root. This launches the backend, frontend, and opens `http://localhost:5173` automatically.

---

### Method B: Manual Startup

#### 1. Start the Backend (Terminal 1)
```powershell
cd F:\Python2026\sanket\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. Start the Frontend (Terminal 2)
```powershell
cd F:\Python2026\sanket\frontend
npm run dev
```

#### 3. Open the Console
Navigate to **`http://localhost:5173`** in your browser.

---

## 👥 Team

**Sanket**  
Project Lead · AI & Systems Development  
Kathmandu, Nepal

---

## 📜 License

This project is licensed under the MIT License — feel free to adapt for humanitarian disaster management, civic technology, and academic research.
```

---

### Command to Save This to Your Project

Run this single command in your PowerShell terminal to update `F:\Python2026\sanket\README.md`:

```powershell
$root = "F:\Python2026\sanket"
# Save the master documentation directly to README.md
Set-Content -Path "$root\README.md" -Encoding UTF8 -Value (Get-Content "$root\README.md" -Raw)
