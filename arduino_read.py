import serial
import json
import time

PORTS = [
    "COM3",  # UNO (change if needed)
    "COM4",  # NANO
    "COM5",  # MEGA
    "COM6"   # ESP32
]

BAUD = 9600

connections = []

for p in PORTS:
    try:
        connections.append(serial.Serial(p, BAUD, timeout=1))
        print(f"Connected: {p}")
    except:
        print(f"Failed: {p}")

def read_line(ser):
    try:
        line = ser.readline().decode().strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    except:
        return None

while True:
    for ser in connections:
        data = read_line(ser)
        if data:
            print("Received:", data)
    time.sleep(0.5)