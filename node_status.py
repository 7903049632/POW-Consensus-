import serial
import time

arduino = serial.Serial('COM9',9600,timeout=1)

time.sleep(2)

while True:

    data = arduino.readline().decode().strip()

    if data:

        print(data)

        if "Node Status : IDLE" in data:
            print("Node Available")

        elif "Node Status : BUSY" in data:
            print("Node Busy")
