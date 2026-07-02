import csv
from full_system import run_once

def run_experiment():
    with open("final_dataset.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Epoch","Miner","Hash"])

        for i in range(600):
            result = run_once(i)
            writer.writerow(result)

    print("Dataset created")