import serial
import random
import hashlib
import time

print("FULL SYSTEM STARTED")

##############################
# CONFIG
##############################

PORT = 'COM9'
BLOCK_SIZE = 5000

##############################
# SERIAL CONNECTION
##############################

try:
    arduino = serial.Serial(PORT, 9600, timeout=1)
    time.sleep(2)
except Exception as e:
    print("Arduino connection failed:", e)
    arduino = None

##############################
# TX GENERATOR
##############################

def generate_tx():
    return random.randint(300, 800)

##############################
# SAFE UNO STATUS READER
##############################

def get_uno_status():
    status = "IDLE"

    if arduino is None:
        return "IDLE"

    try:
        start = time.time()

        while time.time() - start < 2:

            if arduino.in_waiting:
                data = arduino.readline().decode(errors='ignore').strip()

                if "BUSY" in data:
                    status = "BUSY"
                elif "IDLE" in data:
                    status = "IDLE"

    except Exception as e:
        print("UNO Serial Error:", e)
        status = "IDLE"

    return status

##############################
# PROOF OF WORK
##############################

def mine(data, difficulty):
    nonce = 0
    prefix = "0" * difficulty
    start = time.time()

    while True:
        text = data + str(nonce)
        h = hashlib.sha256(text.encode()).hexdigest()

        if h.startswith(prefix):
            return time.time() - start

        nonce += 1

##############################
# RUN ONE EPOCH
##############################

def run_epoch(epoch, difficulty):

    # -----------------------
    # BLOCK CREATION
    # -----------------------
    size = 0
    tx_count = 0

    while size < BLOCK_SIZE:
        size += generate_tx()
        tx_count += 1

    block_data = f"BLOCK_{epoch}"

    # -----------------------
    # NODE STATUS
    # -----------------------
    status = {}

    status["UNO"] = get_uno_status()
    status["NANO"] = random.choice(["BUSY", "IDLE"])
    status["MEGA"] = random.choice(["BUSY", "IDLE"])

    print("\nEpoch:", epoch)
    print("Status:", status)

    # -----------------------
    # ACTIVE MINERS
    # -----------------------
    active = [node for node in status if status[node] == "IDLE"]

    # -----------------------
    # MINING PROCESS
    # -----------------------
    winner = "NONE"
    mining_time = 0

    if active:
        results = {}

        for node in active:
            print(node, "mining...")
            t = mine(block_data, difficulty)
            results[node] = t

        winner = min(results, key=results.get)
        mining_time = results[winner]

        print("Winner:", winner)

    else:
        print("No Miner Available")

    # -----------------------
    # RETURN DATA ROW
    # -----------------------
    return {
        "Epoch": epoch,
        "Difficulty": difficulty,
        "Tx_Count": tx_count,
        "Block_Size": size,
        "UNO": status["UNO"],
        "NANO": status["NANO"],
        "MEGA": status["MEGA"],
        "Winner": winner,
        "Mining_Time": mining_time
    }

##############################
# CLEANUP FUNCTION
##############################

def close_system():
    if arduino:
        arduino.close()
    print("\nSYSTEM CLOSED")