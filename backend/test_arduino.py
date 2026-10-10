import serial
import time

print("--> Opening COM3 at 115200 baud...")
try:
    with serial.Serial("COM3", 115200, timeout=3) as ser:
        print("--> Port opened. Waiting 2s for Arduino bootloader...")
        time.sleep(2.0)
        ser.reset_input_buffer()
        print("--> Reading 5 lines of incoming data:\n")
        for i in range(5):
            raw = ser.readline().decode("utf-8", errors="replace").strip()
            print(f"[{i+1}] {raw}")
except Exception as e:
    print(f"\n--> ERROR: {e}")
