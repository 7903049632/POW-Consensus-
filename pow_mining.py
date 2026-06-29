import hashlib
import random
import time

print("⛏ Proof of Work Mining Simulation Started")

# -----------------------
# Block data (dummy)
# -----------------------
block_data = "IoT_Blockchain_Block_Data"

# -----------------------
# Difficulty
# -----------------------
DIFFICULTY = 2  # change 1-5 later

prefix = "0" * DIFFICULTY

# -----------------------
# Nodes (with status)
# -----------------------
nodes = {
    "UNO": random.choice(["IDLE", "BUSY"]),
    "NANO": random.choice(["IDLE", "BUSY"]),
    "MEGA": random.choice(["IDLE", "BUSY"])
}

print("\nNode Status:")
for n, s in nodes.items():
    print(n, ":", s)

# -----------------------
# Mining function
# -----------------------
def mine(node_name):
    nonce = 0

    start = time.time()

    while True:
        text = block_data + str(nonce)
        hash_result = hashlib.sha256(text.encode()).hexdigest()

        if hash_result.startswith(prefix):
            end = time.time()
            return nonce, hash_result, end - start

        nonce += 1

# -----------------------
# Mining competition
# -----------------------
results = {}

for node, status in nodes.items():
    if status == "IDLE":
        print(f"\n{node} started mining...")

        nonce, hash_result, mining_time = mine(node)

        results[node] = {
            "nonce": nonce,
            "hash": hash_result,
            "time": mining_time
        }

        print(f"{node} solved block!")
        print("Nonce:", nonce)
        print("Hash:", hash_result[:20], "...")
        print("Time:", mining_time, "sec")

    else:
        print(f"\n{node} is BUSY → cannot mine")

# -----------------------
# Winner selection
# -----------------------
if results:
    winner = min(results, key=lambda x: results[x]["time"])

    print("\n🏆 WINNER:", winner)
else:
    print("\nNo node mined the block")