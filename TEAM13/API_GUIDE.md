# Team 13: Data Analytics & Reports - API Integration Guide

This guide is intended for Teams 3, 6, 8, and 10. It specifies how your services can push (`POST`) data directly to our mock analytics API to verify integration workflows dynamically before connecting to production databases.

---

## Running the API Server
Before posting data, ensure our mock backend is actively running.
```bash
# from OS_CBP (workspace root)
uvicorn TEAM13.api.api:app --reload

# from OS_CBP/TEAM13
uvicorn api.api:app --reload
```
By default, the server runs on `http://127.0.0.1:8000`. All payloads sent here will automatically seed into our Dashboard JSON layers.

---

## Posting Data (Webhooks)

### 1. Register a Vehicle (Team 3)
Team 3 can push new registered vehicles to our database.
*   **Endpoint:** `POST /api/v1/vehicles`
*   **Payload Format:**
```json
{
  "vehicle_id": "KA01AB1234",
  "owner_name": "John Doe",
  "owner_type": "Student",
  "vehicle_type": "Car",
  "department": "Engineering",
  "id_number": "STU123456",
  "phone_number": "+919876543210"
}
```

### 2. Register a Location/Camera Zone (Team 6)
Team 6 maps tracking zones which we use for Hotspot Analysis.
*   **Endpoint:** `POST /api/v1/locations`
*   **Payload Format:**
```json
{
  "zone_id": "Z001",
  "zone_name": "Main Gate",
  "speed_limit_kmph": 20,
  "location_type": "Entry"
}
```

### 3. Log an Overspeeding Violation (Team 8)
Team 8's AI engine detects a speed anomaly and logs it directly to our system.
*   **Endpoint:** `POST /api/v1/violations`
*   **Payload Format:**
```json
{
  "violation_id": "VIO-000001",
  "vehicle_id": "KA01AB1234",
  "zone_id": "Z001",
  "detected_speed_kmph": 35.5,
  "speed_limit_kmph": 20,
  "overspeed_delta_kmph": 15.5,
  "severity": "Medium",
  "timestamp": "2024-03-01T08:30:00+00:00",
  "date": "2024-03-01",
  "time_of_day": "Morning",
  "status": "Fine Issued"
}
```
> **Important:** Ensure `timestamp` is exactly in ISO-8601 UTC format.

### 4. Issue or Update a Fine (Team 10)
Team 10's Fine Management system issues penalties which we track for revenue generated vs pending.
*   **Endpoint:** `POST /api/v1/fines`
*   **Payload Format:**
```json
{
  "fine_id": "FINE-000001",
  "violation_id": "VIO-000001",
  "vehicle_id": "KA01AB1234",
  "amount_inr": 500,
  "status": "Pending",
  "issued_on": "2024-03-01",
  "final_amount_inr": 0
}
```
> **Important:** Set `status` strictly to either `"Paid"` or `"Pending"`.

---

## Verifying the Feed
Once you receive a `200 OK` response with `{"status": "success"}`, open our interactive Dashboard to verify the data graphs dynamically updated!
```bash
# from OS_CBP (workspace root)
python -m streamlit run TEAM13/dashboard/app.py

# from OS_CBP/TEAM13
python -m streamlit run dashboard/app.py
```
