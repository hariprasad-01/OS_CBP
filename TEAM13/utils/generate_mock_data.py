import json, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = datetime(2024, 1, 1, tzinfo=timezone.utc)
END_DATE   = datetime(2024, 3, 15, tzinfo=timezone.utc)

def random_date(start, end): return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def build_locations():
    return [{"zone_id": f"Z00{i}", "zone_name": f"Gate {i}", "speed_limit_kmph": 20, "location_type": "Entry"} for i in range(1, 11)]

def build_vehicles():
    departments = ["Engineering", "Science", "Arts", "Administration", "Management"]
    vehicles = []
    for i in range(1, 201):
        o_type = "Student" if i > 40 else "Faculty"
        id_num = f"STU{i:06d}" if o_type == "Student" else f"FAC{i:04d}"
        phone = f"+9198{random.randint(10000000, 99999999)}"
        vehicles.append({
            "vehicle_id": f"KA01AB{i:04d}",
            "owner_name": f"User {i}",
            "owner_type": o_type,
            "vehicle_type": random.choice(["Car", "Bike"]),
            "department": random.choice(departments),
            "id_number": id_num,
            "phone_number": phone
        })
    return vehicles

def build_violations(vehicles, locations):
    rows = []
    for i in range(1, 1001):
        ts = random_date(START_DATE, END_DATE)
        rows.append({
            "violation_id": f"VIO-{i:06d}",
            "vehicle_id": random.choice(vehicles)["vehicle_id"],
            "zone_id": random.choice(locations)["zone_id"],
            "detected_speed_kmph": 35.5,
            "speed_limit_kmph": 20,
            "overspeed_delta_kmph": 15.5,
            "severity": "Medium",
            "timestamp": ts.isoformat(),
            "date": ts.strftime("%Y-%m-%d"),
            "time_of_day": "Morning",
            "status": "Fine Issued",
        })
    return rows

def build_fines(violations):
    eligible = [v for v in violations if v["status"] == "Fine Issued"]
    fines = []
    for i, v in enumerate(random.sample(eligible, 300)):
        status = random.choices(["Paid", "Pending"], weights=[0.7, 0.3])[0]
        final_amt = 500 if status == "Paid" else 0
        fines.append({"fine_id": f"FINE-{i:06d}", "violation_id": v["violation_id"], "vehicle_id": v["vehicle_id"], "amount_inr": 500, "status": status, "issued_on": v["date"], "final_amount_inr": final_amt})
    return fines

def save_json(data, filename):
    with open(OUTPUT_DIR / filename, "w") as f: json.dump(data, f)
    print(f"Saved {len(data)} to {filename}")

if __name__ == "__main__":
    v = build_vehicles(); save_json(v, "vehicles.json")
    l = build_locations(); save_json(l, "locations.json")
    vio = build_violations(v, l); save_json(vio, "violations.json")
    save_json(build_fines(vio), "fines.json")
