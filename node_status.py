status = {
    "UNO": "UNKNOWN",
    "NANO": "UNKNOWN",
    "MEGA": "UNKNOWN",
    "ESP32": "UNKNOWN"
}

def update(node, value):
    status[node] = value

def get_all():
    return status