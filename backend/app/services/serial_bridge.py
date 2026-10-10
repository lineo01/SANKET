import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import serial
import serial.tools.list_ports
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.db_models import SensorReading

class ArduinoSerialBridge:
    """
    Background USB Serial worker that reads Arduino UNO / DHT11 telemetry.
    """
    _thread: Optional[threading.Thread] = None
    _running: bool = False
    latest_telemetry: Dict[str, Any] = {
        "node_id": "EDGE-UNO-01",
        "water_raw": 0,
        "water_level_cm": 0.0,
        "simulated_river_m": 2.40,
        "temperature_c": 26.0,
        "humidity_percent": 75.0,
        "connected": False,
        "port": "NONE",
        "timestamp": None
    }

    @classmethod
    def start_listener(cls, baud_rate: int = 115200):
        if cls._running:
            return
        cls._running = True
        cls._thread = threading.Thread(target=cls._serial_worker, args=(baud_rate,), daemon=True)
        cls._thread.start()

    @classmethod
    def _find_arduino_port(cls) -> Optional[str]:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            desc = p.description.lower()
            if "arduino" in desc or "ch340" in desc or "usb-serial" in desc or "cp210" in desc or "com" in p.device.lower():
                return p.device
        return ports[0].device if ports else None

    @classmethod
    def _serial_worker(cls, baud_rate: int):
        while cls._running:
            port = cls._find_arduino_port()
            if not port:
                cls.latest_telemetry["connected"] = False
                time.sleep(2.0)
                continue

            try:
                with serial.Serial(port, baud_rate, timeout=2.0) as ser:
                    cls.latest_telemetry["connected"] = True
                    cls.latest_telemetry["port"] = port
                    ser.reset_input_buffer()

                    while cls._running:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line.startswith("{") and line.endswith("}"):
                            try:
                                data = json.loads(line)
                                cls.latest_telemetry.update(data)
                                cls.latest_telemetry["connected"] = True
                                cls.latest_telemetry["port"] = port
                                cls.latest_telemetry["timestamp"] = datetime.utcnow().isoformat()

                                db: Session = SessionLocal()
                                try:
                                    reading = SensorReading(
                                        node_id=data.get("node_id", "EDGE-UNO-01"),
                                        water_level_cm=float(data.get("water_level_cm", 0.0)),
                                        rainfall_mm_per_hr=0.0,
                                        temperature_c=float(data.get("temperature_c", 0.0)),
                                        humidity_percent=float(data.get("humidity_percent", 0.0)),
                                        battery_percent=98.0,
                                        timestamp=datetime.utcnow()
                                    )
                                    db.add(reading)
                                    db.commit()
                                finally:
                                    db.close()
                            except Exception:
                                pass
            except Exception:
                cls.latest_telemetry["connected"] = False
                time.sleep(2.0)
