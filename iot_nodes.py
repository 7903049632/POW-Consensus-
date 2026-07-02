import csv
import time
import random

FILENAME = "final_dataset.csv"

fields = [
    "Epoch",
    "Difficulty",
    "Tx_Count",
    "Block_Size",
    "UNO",
    "NANO",
    "MEGA",
    "Winner",
    "Mining_Time"
]

nodes = ["UNO", "NANO", "MEGA", "ESP32"]

def simulate_node_status(winner):
    status = {}
    for n in nodes:
        status[n] = "MINING" if n == winner else "IDLE"
    return status

def generate_row(epoch):
    difficulty = random.randint(1, 3)
    tx = random.randint(5, 25)
    block_size = random.randint(3000, 8000)

    winner = random.choice(nodes)
    mining_time = round(random.uniform(0.00005, 0.5), 6)

    status = simulate_node_status(winner)

    return [
        epoch,
        difficulty,
        tx,
        block_size,
        status["UNO"],
        status["NANO"],
        status["MEGA"],
        winner,
        mining_time
    ]

def create_dataset(rows=600):
    with open(FILENAME, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)

        for i in range(rows):
            row = generate_row(i)
            writer.writerow(row)
            print(f"Row {i} written")

if __name__ == "__main__":
    create_dataset()