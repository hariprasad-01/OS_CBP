"""
Team 13 — Client Abstraction Layer
Campus Vehicle Speed Control System

Provides fetch_data(), abstracting whether records come from local mock JSONs
or from external live APIs across Teams 3, 6, 8, and 10.
"""

import os
import json
import requests
from pathlib import Path

# Config switch (can be driven by env vars)
USE_LIVE_API = os.getenv("USE_LIVE_API", "False").lower() in ("true", "1", "t", "yes")

# Simulated Live Endpoints
LIVE_URLS = {
    "vehicles":   os.getenv("TEAM3_URL",  "http://localhost:8000/api/v1/vehicles"),
    "locations":  os.getenv("TEAM6_URL",  "http://localhost:8000/api/v1/locations"),
    "violations": os.getenv("TEAM8_URL",  "http://localhost:8000/api/v1/violations"),
    "fines":      os.getenv("TEAM10_URL", "http://localhost:8000/api/v1/fines"),
}

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def fetch_data(entity: str) -> list | None:
    """
    Fetch requested `entity` records either from remote API or local folder.
    Returns a Python list of dicts, or None if fetching failed.
    """
    if entity not in LIVE_URLS:
        print(f"Unknown entity: {entity}")
        return None

    if USE_LIVE_API:
        try:
            url = LIVE_URLS[entity]
            print(f"Fetching {entity} from LIVE API: {url} ...")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            # Unpack Team envelopes e.g. {"count": x, "data": [...]}
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data
            
        except requests.RequestException as e:
            print(f"⚠️ Live API failed for {entity}: {e}. Falling back to MOCK DATA.")
            return _fetch_local(entity)
    else:
        return _fetch_local(entity)

def _fetch_local(entity: str) -> list | None:
    """Read local JSON stub."""
    path = DATA_DIR / f"{entity}.json"
    if not path.exists():
        print(f"Local file not found: {path}")
        return None
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Unpackenvelope if mock generator used one
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data if isinstance(data, list) else None
            
    except json.JSONDecodeError as e:
        print(f"Error parsing local {entity}.json: {e}")
        return None

def get_vehicles() -> list | None: return fetch_data("vehicles")
def get_locations() -> list | None: return fetch_data("locations")
def get_violations() -> list | None: return fetch_data("violations")
def get_fines() -> list | None: return fetch_data("fines")

