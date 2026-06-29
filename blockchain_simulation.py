import random
import hashlib
import time

# -------------------------------
# Create Transactions
# -------------------------------

BLOCK_SIZE = 5 * 1024      # 5KB
current_size = 0
transactions = []

while current_size < BLOCK_SIZE:

    tx_size = random.randint(400,600)

    transactions.append(tx_size)

    current_size += tx_size


print("\nBlock Created")
print("Transactions :",len(transactions))
print("Block Size :",current_size,"bytes")


# -------------------------------
# Assume node status
# -------------------------------

node_status = "IDLE"


# -------------------------------
# PoW Mining
# -------------------------------

def mine_block(difficulty):

    nonce = 0

    target = "0"*difficulty


    while True:

        text = str(nonce)

        hash_value = hashlib.sha256(
                        text.encode()
                        ).hexdigest()


        if hash_value.startswith(target):

            return nonce,hash_value


        nonce += 1


# -------------------------------
# Mining Decision
# -------------------------------

if node_status=="IDLE":

    print("\nNode Available")
    print("Mining Started")


    nonce,hash_value = mine_block(2)


    print("\nMining Success")

    print("Nonce :",nonce)

    print("Hash :",hash_value)



else:

    print("Node Busy")

    print("Mining Skipped")