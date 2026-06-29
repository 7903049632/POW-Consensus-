import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("final_dataset.csv")

print("Rows:", len(df))

# -------------------------
# 1. Difficulty vs Mining Time
# -------------------------
plt.figure()

avg_time = df.groupby("Difficulty")["Mining_Time"].mean()

plt.plot(avg_time.index, avg_time.values, marker="o")

plt.title("Difficulty vs Mining Time")
plt.xlabel("Difficulty")
plt.ylabel("Avg Mining Time")

plt.show()

# -------------------------
# 2. Winner Distribution
# -------------------------
plt.figure()

df["Winner"].value_counts().plot(kind="bar")

plt.title("Node Winning Frequency")
plt.xlabel("Node")
plt.ylabel("Wins")

plt.show()

# -------------------------
# 3. BUSY vs IDLE Impact
# -------------------------
plt.figure()

busy = (df["UNO"]=="BUSY").sum() + (df["NANO"]=="BUSY").sum() + (df["MEGA"]=="BUSY").sum()
idle = (df["UNO"]=="IDLE").sum() + (df["NANO"]=="IDLE").sum() + (df["MEGA"]=="IDLE").sum()

plt.bar(["BUSY","IDLE"], [busy, idle])

plt.title("System Status Distribution")
plt.show()