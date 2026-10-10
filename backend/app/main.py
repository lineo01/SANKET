import time
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.routes import router
from app.services.serial_bridge import ArduinoSerialBridge
from app.services.dhm_scraper import DHMScraperService

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Offline-first AI flood early warning system foundation for Nepal",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_STR)

def _background_dhm_updater():
    """Background loop that updates DHM hydrograph telemetry every 20 seconds."""
    time.sleep(3.0)  # Initial boot grace period
    while True:
        try:
            db = SessionLocal()
            try:
                DHMScraperService.fetch_live_dhm_reading(db)
            finally:
                db.close()
        except Exception as e:
            print(f"[DHM Background Scraper Warning]: {e}")
        time.sleep(20.0)

@app.on_event("startup")
def startup_event():
    # 1. Start USB Serial listener for Arduino UNO/DHT11
    ArduinoSerialBridge.start_listener(baud_rate=115200)

    # 2. Start Automatic Background Scraper Loop (runs continuously)
    scraper_thread = threading.Thread(target=_background_dhm_updater, daemon=True)
    scraper_thread.start()
