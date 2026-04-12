import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, Field

# Adjust path so API can find data
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Campus Speed API", description="Mock backend Team 13")


class VehicleIn(BaseModel):
    vehicle_id: str = Field(min_length=1)
    owner_name: str = Field(min_length=1)
    owner_type: str = Field(min_length=1)
    vehicle_type: str = Field(min_length=1)
    department: str = Field(min_length=1)
    id_number: str = Field(min_length=1)
    phone_number: str = Field(min_length=1)


class LocationIn(BaseModel):
    zone_id: str = Field(min_length=1)
    zone_name: str = Field(min_length=1)
    speed_limit_kmph: float
    location_type: str = Field(min_length=1)


class ViolationIn(BaseModel):
    violation_id: str = Field(min_length=1)
    vehicle_id: str = Field(min_length=1)
    zone_id: str = Field(min_length=1)
    detected_speed_kmph: float
    speed_limit_kmph: float
    overspeed_delta_kmph: float
    severity: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    date: str = Field(min_length=1)
    time_of_day: str = Field(min_length=1)
    status: str = Field(min_length=1)


class FineIn(BaseModel):
    fine_id: str = Field(min_length=1)
    violation_id: str = Field(min_length=1)
    vehicle_id: str = Field(min_length=1)
    amount_inr: float
    status: str = Field(min_length=1)
    issued_on: str = Field(min_length=1)
    final_amount_inr: float

def _load_json(name: str):
    path = DATA_DIR / name
    if not path.exists(): return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(name: str, data: list):
    path = DATA_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.get("/api/v1/vehicles")
def get_vehicles(owner_type: Optional[str] = None):
    data = _load_json("vehicles.json")
    if owner_type: data = [v for v in data if v.get("owner_type") == owner_type]
    return {"count": len(data), "data": data}

@app.post("/api/v1/vehicles")
def post_vehicle(vehicle: VehicleIn):
    data = _load_json("vehicles.json")
    if any(v.get("vehicle_id") == vehicle.vehicle_id for v in data):
        raise HTTPException(status_code=409, detail="vehicle_id already exists")
    data.append(vehicle.model_dump())
    _save_json("vehicles.json", data)
    return {"status": "success", "message": "Vehicle added successfully"}

@app.get("/api/v1/locations")
def get_locations(): return {"data": _load_json("locations.json")}

@app.post("/api/v1/locations")
def post_location(location: LocationIn):
    data = _load_json("locations.json")
    if any(v.get("zone_id") == location.zone_id for v in data):
        raise HTTPException(status_code=409, detail="zone_id already exists")
    data.append(location.model_dump())
    _save_json("locations.json", data)
    return {"status": "success", "message": "Location added successfully"}

@app.get("/api/v1/violations")
def get_violations(zone_id: Optional[str] = None):
    data = _load_json("violations.json")
    if zone_id: data = [v for v in data if v.get("zone_id") == zone_id]
    return {"count": len(data), "data": data}

@app.post("/api/v1/violations")
def post_violation(violation: ViolationIn):
    data = _load_json("violations.json")
    if any(v.get("violation_id") == violation.violation_id for v in data):
        raise HTTPException(status_code=409, detail="violation_id already exists")
    data.append(violation.model_dump())
    _save_json("violations.json", data)
    return {"status": "success", "message": "Violation added successfully"}

@app.get("/api/v1/fines")
def get_fines(): return {"data": _load_json("fines.json")}

@app.post("/api/v1/fines")
def post_fine(fine: FineIn):
    data = _load_json("fines.json")
    if any(v.get("fine_id") == fine.fine_id for v in data):
        raise HTTPException(status_code=409, detail="fine_id already exists")
    data.append(fine.model_dump())
    _save_json("fines.json", data)
    return {"status": "success", "message": "Fine added successfully"}
