import serial
import time
import hashlib

print("Program Started")

arduino = serial.Serial('COM9', 9600, timeout=1)
time.sleep(2)

def mine_block():
    print("⛏️ Mining started...")

    nonce = 0
    difficulty = "0000"

    while True:
        text = str(nonce).encode()
        hash_result = hashlib.sha256(text).hexdigest()

        if hash_result[:4] == difficulty:
            print("✅ Block Mined!")
            print("Hash:", hash_result)
            break

        nonce += 1

while True:
    data = arduino.readline().decode(errors='ignore').strip()

    if data:
        print("Node Status:", data)

        if data == "IDLE":
            mine_block()

        elif data == "BUSY":
            print("⛔ Mining Skipped")

    time.sleep(1)