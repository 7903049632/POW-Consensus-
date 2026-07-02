import hashlib

def create_header(index, data, prev_hash):
    return f"{index}|{data}|{prev_hash}"

def validate_hash(hash_value, difficulty=4):
    return hash_value.startswith("0" * difficulty)