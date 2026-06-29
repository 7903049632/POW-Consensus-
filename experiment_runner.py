from full_system import run_epoch, close_system
import pandas as pd

all_data = []

for difficulty in range(1, 7):
    print("\n====================")
    print("DIFFICULTY:", difficulty)
    print("====================")

    for epoch in range(100):
        row = run_epoch(epoch, difficulty)
        row["Difficulty"] = difficulty
        all_data.append(row)

df = pd.DataFrame(all_data)
df.to_csv("final_dataset.csv", index=False)

close_system()

print("DONE: 600 ROW DATASET GENERATED")