import time
import hashlib

class Block:
    def __init__(self, index, data, prev_hash, nonce, miner):
        self.index = index
        self.data = data
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.miner = miner
        self.timestamp = time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        text = f"{self.index}{self.data}{self.prev_hash}{self.nonce}{self.miner}"
        return hashlib.sha256(text.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 4

    def last_hash(self):
        if not self.chain:
            return "0"
        return self.chain[-1].hash

    def add_block(self, block):
        self.chain.append(block)
        print("\n⛓️ BLOCK ADDED TO CHAIN")
        print("Index:", block.index)
        print("Miner:", block.miner)
        print("Hash:", block.hash[:20], "...\n")