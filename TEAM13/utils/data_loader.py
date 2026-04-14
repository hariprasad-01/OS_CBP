"""
Team 13 — Data Loader & Validator
"""
import pandas as pd
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from api.client import fetch_data

REQUIRED_KEYS = {
    "vehicles": ["vehicle_id", "owner_name", "owner_type", "vehicle_type", "department", "id_number", "phone_number"],
    "violations": ["violation_id", "vehicle_id", "zone_id", "detected_speed_kmph", "speed_limit_kmph", "overspeed_delta_kmph", "severity", "timestamp", "date", "time_of_day", "status"],
    "fines": ["fine_id", "violation_id", "vehicle_id", "amount_inr", "status", "issued_on", "final_amount_inr"],
    "locations": ["zone_id", "zone_name", "speed_limit_kmph", "location_type"],
}

def load_data() -> dict[str, pd.DataFrame | None]:
    frames: dict[str, pd.DataFrame | None] = {}
    
    entities = ["vehicles", "violations", "fines", "locations"]
    
    for name in entities:
        raw = fetch_data(name)
        if raw is None:
            frames[name] = None
            continue
            
        df = pd.DataFrame(raw)
        if name == "violations" and "evidence" in df.columns:
            df = pd.json_normalize(raw, max_level=1)
        if name == "locations" and "coordinates" in df.columns:
            df["latitude"]  = df["coordinates"].apply(lambda c: c.get("latitude") if isinstance(c, dict) else None)
            df["longitude"] = df["coordinates"].apply(lambda c: c.get("longitude") if isinstance(c, dict) else None)
            df.drop(columns=["coordinates"], inplace=True)

        required = REQUIRED_KEYS[name]
        missing_cols = [col for col in required if col not in df.columns]
        if missing_cols:
            print(f"Invalid {name} dataset: missing columns {missing_cols}")
            frames[name] = None
            continue

        df = df[required].copy()
        df = df.dropna(subset=[required[0]])

        if name == "violations":
            numeric_cols = ["detected_speed_kmph", "speed_limit_kmph", "overspeed_delta_kmph"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
            df = df.dropna(subset=["violation_id", "vehicle_id", "zone_id", "timestamp"])

        if name == "fines":
            numeric_cols = ["amount_inr", "final_amount_inr"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(subset=["fine_id", "violation_id", "vehicle_id", "amount_inr"])

        frames[name] = df
    return frames
