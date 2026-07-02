"""
POW-Consensus: IoT-Based Blockchain Mining System with Machine Learning
Production coordinator for Arduino UNO, Arduino MEGA, ESP32, and Arduino NANO.

Hardware protocol used by this file:
UNO  -> SENSOR,Epoch,Temperature,Humidity,Tx_Count,Difficulty
MEGA <- MINE:temp,humidity,tx,difficulty
MEGA -> MINED|MEGA|nonce|hash
ESP32 <- MINE:temp,humidity,tx,difficulty
ESP32 -> MINED|ESP32|nonce|hash
NANO <- MINED:MEGA or MINED:ESP32
NANO -> VALIDATED|TRUE or VALIDATED|FALSE
"""

from __future__ import annotations

import csv
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    import serial
    from serial import SerialException
except ImportError as exc:
    raise SystemExit(
        "pyserial is required. Install it with: pip install pyserial"
    ) from exc


UNO_PORT = "COM5"
MEGA_PORT = "COM6"
ESP32_PORT = "COM7"
NANO_PORT = "COM9"
BAUD_RATE = 9600

TARGET_ROWS = 900
OUTPUT_FILE = "final_dataset.csv"

SERIAL_TIMEOUT_SECONDS = 0.20
BOARD_BOOT_DELAY_SECONDS = 2.50
SENSOR_READ_TIMEOUT_SECONDS = 8.00
MINER_READ_TIMEOUT_SECONDS = 10.00
VALIDATOR_READ_TIMEOUT_SECONDS = 5.00

MAX_SENSOR_ATTEMPTS = 5
MAX_MINING_ATTEMPTS = 3
MAX_VALIDATION_ATTEMPTS = 3

STARTUP_MESSAGES = {
    "UNO_SENSOR_NODE_READY",
    "MEGA_READY",
    "ESP32_READY",
    "NANO_READY",
    "MEGA_MINING",
    "ESP32_MINING",
}

DATASET_COLUMNS = [
    "Epoch",
    "Temp",
    "Humidity",
    "Tx",
    "Difficulty",
    "MEGA_Response_ms",
    "ESP32_Response_ms",
    "MEGA_Score",
    "ESP32_Score",
    "Winner",
    "Validation",
]


@dataclass(frozen=True)
class SensorReading:
    epoch: int
    temp: float
    humidity: float
    tx: int
    difficulty: int


@dataclass(frozen=True)
class MiningResult:
    node: str
    nonce: int
    block_hash: str
    response_ms: float


def clean_line(raw: bytes) -> str:
    return raw.decode("utf-8", errors="ignore").strip()


def is_startup_message(line: str) -> bool:
    return line.strip().upper() in STARTUP_MESSAGES


def split_protocol_line(line: str) -> list[str]:
    delimiter = "|" if "|" in line else ","
    return [part.strip() for part in line.split(delimiter)]


def parse_sensor_line(line: str) -> Optional[SensorReading]:
    if not line or is_startup_message(line):
        return None

    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 6 or parts[0].upper() != "SENSOR":
        return None

    try:
        return SensorReading(
            epoch=int(parts[1]),
            temp=float(parts[2]),
            humidity=float(parts[3]),
            tx=int(parts[4]),
            difficulty=int(parts[5]),
        )
    except ValueError:
        return None


def parse_mining_line(line: str, expected_node: str, response_ms: float) -> Optional[MiningResult]:
    if not line or is_startup_message(line):
        return None

    parts = split_protocol_line(line)
    if len(parts) != 4:
        return None

    if parts[0].upper() != "MINED" or parts[1].upper() != expected_node.upper():
        return None

    try:
        nonce = int(parts[2])
    except ValueError:
        return None

    block_hash = parts[3]
    if not block_hash:
        return None

    return MiningResult(
        node=expected_node.upper(),
        nonce=nonce,
        block_hash=block_hash,
        response_ms=round(response_ms, 3),
    )


def parse_validation_line(line: str) -> Optional[str]:
    if not line or is_startup_message(line):
        return None

    normalized = line.strip().upper()

    if normalized in {"APPROVED", "TRUE", "VALID"}:
        return "TRUE"

    if normalized in {"REJECTED", "FALSE", "INVALID"}:
        return "FALSE"

    parts = [part.strip().upper() for part in split_protocol_line(line)]
    if len(parts) == 2 and parts[0] == "VALIDATED" and parts[1] in {"TRUE", "FALSE"}:
        return parts[1]

    return None


def open_serial_port(port: str, label: str) -> serial.Serial:
    try:
        ser = serial.Serial(
            port=port,
            baudrate=BAUD_RATE,
            timeout=SERIAL_TIMEOUT_SECONDS,
            write_timeout=2.0,
        )
        print(f"[OK] {label} connected on {port}")
        return ser
    except SerialException as exc:
        raise RuntimeError(f"Could not open {label} on {port}: {exc}") from exc


def reset_input_buffers(ports: Iterable[serial.Serial]) -> None:
    for ser in ports:
        try:
            ser.reset_input_buffer()
        except SerialException:
            pass


def safe_write_line(ser: serial.Serial, message: str, label: str) -> bool:
    try:
        ser.write((message + "\n").encode("utf-8"))
        ser.flush()
        return True
    except SerialException as exc:
        print(f"[WARN] Write failed for {label}: {exc}")
        return False


def close_ports_safely(ports: Iterable[serial.Serial]) -> None:
    for ser in ports:
        try:
            if ser and ser.is_open:
                ser.close()
        except SerialException:
            pass


def read_until_valid_line(
    ser: serial.Serial,
    label: str,
    timeout_seconds: float,
    parser,
    show_raw: bool = False,
) -> Optional[object]:
    deadline = time.perf_counter() + timeout_seconds

    while time.perf_counter() < deadline:
        try:
            raw = ser.readline()
        except SerialException as exc:
            print(f"[WARN] Read failed for {label}: {exc}")
            return None

        if not raw:
            continue

        line = clean_line(raw)

        if show_raw and line:
            print(f"{label} RAW: {line}")

        if not line or is_startup_message(line):
            continue

        parsed = parser(line)
        if parsed is not None:
            return parsed

        print(f"[INFO] Ignored {label} line: {line}")

    return None


def read_sensor(uno: serial.Serial) -> Optional[SensorReading]:
    for attempt in range(1, MAX_SENSOR_ATTEMPTS + 1):
        reading = read_until_valid_line(
            ser=uno,
            label="UNO",
            timeout_seconds=SENSOR_READ_TIMEOUT_SECONDS,
            parser=parse_sensor_line,
            show_raw=True,
        )

        if isinstance(reading, SensorReading):
            return reading

        print(f"[WARN] Sensor read attempt {attempt}/{MAX_SENSOR_ATTEMPTS} failed")

    return None


def mine_on_node(
    ser: serial.Serial,
    node_name: str,
    sensor: SensorReading,
) -> Optional[MiningResult]:
    command = f"MINE:{sensor.temp},{sensor.humidity},{sensor.tx},{sensor.difficulty}"

    for attempt in range(1, MAX_MINING_ATTEMPTS + 1):
        try:
            ser.reset_input_buffer()
        except SerialException:
            pass

        start = time.perf_counter()

        if not safe_write_line(ser, command, node_name):
            continue

        def parser(line: str) -> Optional[MiningResult]:
            response_ms = (time.perf_counter() - start) * 1000.0
            return parse_mining_line(line, node_name, response_ms)

        result = read_until_valid_line(
            ser=ser,
            label=node_name,
            timeout_seconds=MINER_READ_TIMEOUT_SECONDS,
            parser=parser,
            show_raw=True,
        )

        if isinstance(result, MiningResult):
            return result

        print(f"[WARN] {node_name} mining attempt {attempt}/{MAX_MINING_ATTEMPTS} failed")

    return None


def validate_winner(nano: serial.Serial, winner: str) -> Optional[str]:
    command = f"MINED:{winner.upper()}"

    for attempt in range(1, MAX_VALIDATION_ATTEMPTS + 1):
        try:
            nano.reset_input_buffer()
        except SerialException:
            pass

        if not safe_write_line(nano, command, "NANO"):
            continue

        result = read_until_valid_line(
            ser=nano,
            label="NANO",
            timeout_seconds=VALIDATOR_READ_TIMEOUT_SECONDS,
            parser=parse_validation_line,
            show_raw=True,
        )

        if result in {"TRUE", "FALSE"}:
            return str(result)

        print(f"[WARN] Validation attempt {attempt}/{MAX_VALIDATION_ATTEMPTS} failed")

    return None


def hash_strength(block_hash: str) -> float:
    token = block_hash.strip()

    if not token:
        return 0.0

    try:
        value = int(token, 16 if re.search(r"[A-Fa-f]", token) else 10)
    except ValueError:
        value = sum(ord(ch) for ch in token)

    return 1.0 / (1.0 + max(value, 0))


def mining_score(result: MiningResult) -> float:
    speed_component = 100000.0 / max(result.response_ms, 1.0)
    nonce_component = 1000.0 / (1.0 + max(result.nonce, 0))

    return round(speed_component + nonce_component + hash_strength(result.block_hash), 6)


def choose_winner(mega_result: MiningResult, esp32_result: MiningResult) -> str:
    if mega_result.response_ms <= esp32_result.response_ms:
        return "MEGA"

    return "ESP32"


def append_row(csv_path: Path, row: dict) -> None:
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DATASET_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def count_existing_rows(csv_path: Path) -> int:
    if not csv_path.exists():
        return 0

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for _ in reader)


def prepare_output_file(csv_path: Path) -> None:
    if csv_path.exists():
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = csv_path.with_name(f"{csv_path.stem}_backup_{timestamp}{csv_path.suffix}")
        os.replace(csv_path, backup_path)
        print(f"[INFO] Existing dataset moved to {backup_path}")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DATASET_COLUMNS)
        writer.writeheader()


def build_dataset_row(
    sensor: SensorReading,
    mega_result: MiningResult,
    esp32_result: MiningResult,
    winner: str,
    validation: str,
) -> dict:
    return {
        "Epoch": sensor.epoch,
        "Temp": round(sensor.temp, 2),
        "Humidity": round(sensor.humidity, 2),
        "Tx": sensor.tx,
        "Difficulty": sensor.difficulty,
        "MEGA_Response_ms": round(mega_result.response_ms, 3),
        "ESP32_Response_ms": round(esp32_result.response_ms, 3),
        "MEGA_Score": mining_score(mega_result),
        "ESP32_Score": mining_score(esp32_result),
        "Winner": winner,
        "Validation": validation,
    }


def collect_dataset() -> None:
    csv_path = Path(OUTPUT_FILE).resolve()
    prepare_output_file(csv_path)

    uno = mega = esp32 = nano = None

    try:
        uno = open_serial_port(UNO_PORT, "UNO Sensor Node")
        mega = open_serial_port(MEGA_PORT, "MEGA Miner Node 1")
        esp32 = open_serial_port(ESP32_PORT, "ESP32 Miner Node 2")
        nano = open_serial_port(NANO_PORT, "NANO Validator Node")

        print(f"[INFO] Waiting {BOARD_BOOT_DELAY_SECONDS:.1f}s for boards to settle...")
        time.sleep(BOARD_BOOT_DELAY_SECONDS)
        reset_input_buffers([uno, mega, esp32, nano])

        valid_rows = 0
        skipped_cycles = 0

        while valid_rows < TARGET_ROWS:
            print(f"\n[INFO] Collecting row {valid_rows + 1}/{TARGET_ROWS}")

            sensor = read_sensor(uno)

            if sensor is None:
                skipped_cycles += 1
                print("[WARN] Skipping cycle: no valid UNO sensor reading")
                continue

            mega_result = mine_on_node(mega, "MEGA", sensor)

            if mega_result is None:
                skipped_cycles += 1
                print("[WARN] Skipping cycle: MEGA did not return a valid mining response")
                continue

            esp32_result = mine_on_node(esp32, "ESP32", sensor)

            if esp32_result is None:
                skipped_cycles += 1
                print("[WARN] Skipping cycle: ESP32 did not return a valid mining response")
                continue

            winner = choose_winner(mega_result, esp32_result)
            validation = validate_winner(nano, winner)

            if validation is None:
                skipped_cycles += 1
                print("[WARN] Skipping cycle: NANO did not return a valid validation response")
                continue

            row = build_dataset_row(sensor, mega_result, esp32_result, winner, validation)
            append_row(csv_path, row)
            valid_rows += 1

            print(
                f"Epoch {sensor.epoch} | Winner:{winner} | "
                f"MEGA {mega_result.response_ms:.2f} ms | "
                f"ESP32 {esp32_result.response_ms:.2f} ms | "
                f"Validation:{validation}"
            )

        final_count = count_existing_rows(csv_path)

        if final_count != TARGET_ROWS:
            raise RuntimeError(
                f"Dataset row count mismatch: expected {TARGET_ROWS}, found {final_count}"
            )

        print(f"\n[COMPLETE] Saved exactly {TARGET_ROWS} rows to {csv_path}")
        print(f"[INFO] Skipped incomplete cycles: {skipped_cycles}")

    except KeyboardInterrupt:
        print("\n[STOPPED] User interrupted dataset collection.")
        sys.exit(130)

    finally:
        close_ports_safely(port for port in [uno, mega, esp32, nano] if port is not None)
        print("[INFO] Serial ports closed safely.")


if __name__ == "__main__":
    collect_dataset()