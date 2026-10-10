import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import serial

class ArduinoSerialBridge:
    """
    Dedicated COM3 Serial Bridge for Arduino Uno (EDGE-UNO-01).
    """
    PORT = "COM3"
    BAUD = 115200
    _running: bool = False
    _thread: Optional[threading.Thread] = None

    latest_telemetry: Dict[str, Any] = {
        "node_id": "EDGE-UNO-01",
        "water_raw": None,
        "water_level_cm": None,
        "simulated_river_m": None,
        "temperature_c": None,
        "humidity_percent": None,
        "connected": False,
        "port": "COM3",
        "timestamp": None
    }

    @classmethod
    def start_listener(cls, baud_rate: int = 115200):
        if cls._running:
            return
        cls._running = True
        cls._thread = threading.Thread(target=cls._worker, daemon=True)
        cls._thread.start()

    @classmethod
    def _worker(cls):
        while cls._running:
            try:
                with serial.Serial(cls.PORT, cls.BAUD, timeout=2.0) as ser:
                    # Give Uno time to complete DTR auto-reset
                    time.sleep(2.0)
                    ser.reset_input_buffer()
                    print(f"\n[Hardware Bridge] Connected to {cls.PORT}. Listening for packets...")

                    while cls._running:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line.startswith("{") and line.endswith("}"):
                            try:
                                data = json.loads(line)
                                cls.latest_telemetry.update({
                                    "node_id": data.get("node_id", "EDGE-UNO-01"),
                                    "water_raw": int(data.get("water_raw", 0)),
                                    "water_level_cm": float(data.get("water_level_cm", 0.0)),
                                    "simulated_river_m": float(data.get("simulated_river_m", 2.2)),
                                    "temperature_c": float(data.get("temperature_c", 0.0)),
                                    "humidity_percent": float(data.get("humidity_percent", 0.0)),
                                    "connected": True,
                                    "port": cls.PORT,
                                    "timestamp": datetime.utcnow().isoformat()
                                })
                            except Exception:
                                pass
            except Exception as e:
                cls.latest_telemetry["connected"] = False
                time.sleep(2.0)
