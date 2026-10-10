"""
Flood alert bridge: reads Arduino JSON over USB serial and serves a live
alarm page to phones on the same Wi-Fi / hotspot. Works fully offline.

Usage:
  pip install pyserial
  python server.py                     # auto-detect Arduino port
  python server.py --port COM4         # or /dev/ttyACM0
  python server.py --simulate          # no Arduino: fake rising river

Testing without touching the sensor (works for the web page AND the Android app):
  - Type 0, 1 or 2 + Enter in this terminal to force that alert level.
    Type auto to hand control back to the sensor.
  - Or open  http://<laptop-ip>:8000/force?level=2   (level=0 | 1 | 2 | auto)
"""
import argparse
import json
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).parent
STALE_AFTER_S = 5

latest = {"ts": 0.0, "data": {}}
lock = threading.Lock()
override = None  # None = follow the sensor; otherwise a forced level 0/1/2


def publish(data):
    with lock:
        latest["ts"] = time.time()
        latest["data"] = data


def set_override(text):
    """Returns a status message, or None if the input isn't valid."""
    global override
    t = str(text).strip().lower()
    if t in ("0", "1", "2"):
        override = int(t)
        return f"Forced alert level {override}"
    if t in ("auto", "a"):
        override = None
        return "Back to sensor control"
    return None


def console():
    print("Test controls: type 0 / 1 / 2 + Enter to force a level, 'auto' to follow the sensor.")
    try:
        for line in sys.stdin:
            if not line.strip():
                continue
            print(set_override(line) or "Type 0, 1, 2 or auto")
    except Exception:
        pass


def find_port():
    from serial.tools import list_ports
    ports = list(list_ports.comports())
    for p in ports:
        desc = f"{p.description} {p.manufacturer or ''}".lower()
        if any(k in desc for k in ("arduino", "ch340", "usb serial", "acm")):
            return p.device
    return ports[0].device if ports else None


def serial_reader(port, baud):
    import serial
    while True:
        try:
            dev = port or find_port()
            if not dev:
                print("No serial port found, retrying...")
                time.sleep(2)
                continue
            print(f"Opening {dev} @ {baud}")
            with serial.Serial(dev, baud, timeout=2) as ser:
                time.sleep(2)  # Uno resets on open
                while True:
                    line = ser.readline().decode(errors="ignore").strip()
                    if not line.startswith("{"):
                        continue
                    try:
                        publish(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"Serial error: {e}; retrying in 2s")
            time.sleep(2)


def simulator():
    level, step = 1.0, 0.25
    while True:
        level += step
        if level >= 6.5 or level <= 1.0:
            step = -step
        alert = 2 if level >= 5.5 else 1 if level >= 4.5 else 0
        publish({
            "node_id": "SIM-01",
            "water_raw": int(level / 6.5 * 700),
            "water_level_cm": round(level / 6.5 * 45, 1),
            "simulated_river_m": round(level, 2),
            "temperature_c": 24.0,
            "humidity_percent": 60.0,
            "alert_level": alert,
        })
        time.sleep(1)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype, code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/data":
            with lock:
                age = time.time() - latest["ts"] if latest["ts"] else None
                out = dict(latest["data"])
            out["online"] = age is not None and age < STALE_AFTER_S
            if override is not None:          # forced test level wins over the sensor
                out["alert_level"] = override
                out["online"] = True
                out.setdefault("node_id", "TEST")
                out["override"] = True
            self._send(json.dumps(out).encode(), "application/json")
        elif u.path == "/force":
            msg = set_override(parse_qs(u.query).get("level", [""])[0])
            if msg:
                print(msg)
                self._send(msg.encode(), "text/plain")
            else:
                self._send(b"use /force?level=0|1|2|auto", "text/plain", 400)
        elif u.path in ("/", "/index.html"):
            self._send((HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self._send(b"not found", "text/plain", 404)


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no traffic sent
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--http", type=int, default=8000)
    ap.add_argument("--simulate", action="store_true")
    args = ap.parse_args()

    target = simulator if args.simulate else (lambda: serial_reader(args.port, args.baud))
    threading.Thread(target=target, daemon=True).start()
    threading.Thread(target=console, daemon=True).start()

    print(f"\nOpen on phones (same Wi-Fi/hotspot):  http://{local_ip()}:{args.http}")
    print(f"Force a level from any browser:       http://{local_ip()}:{args.http}/force?level=2\n")
    ThreadingHTTPServer(("0.0.0.0", args.http), Handler).serve_forever()