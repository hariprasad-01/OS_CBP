# Data Analytics & Reports Module
**Campus Vehicle Speed Control System**

This repository contains the Analytics, Reporting, and Visualisation module. It ingests data from Teams 3, 6, 8, and 10 to provide deep insights into speed violations, revenue collection, and high-risk zones.

---

## 📂 Project Structure

```text
├── api/
│   └── api.py                # FastAPI mock backend simulating data ingestion
├── analytics/
│   └── analytics.py          # Core pandas analytics engine (trends, KPIs, etc.)
├── dashboard/
│   └── app.py                # Streamlit interactive web dashboard
├── data/                     # Data directory (populated by generator)
│   ├── vehicles.json
│   ├── locations.json
│   ├── violations.json
│   └── fines.json
├── utils/
│   ├── data_loader.py        # Validates and loads JSON to pandas DataFrames 
│   ├── report_utils.py       # Functions to generate CSV/TXT reports
│   └── generate_mock_data.py # Script to seed the `data` folder
├── API_GUIDE.md              # Documentation for external teams pushing data
├── requirements.txt          # Python dependencies
└── README.md                 # You are here
```

---

## 🛠️ Setup Instructions

Use one of the two command styles below based on your current directory.

**1. Install Dependencies**
Ensure you have Python 3.9+ installed. Run:
```bash
# from OS_CBP (workspace root)
pip install -r TEAM13/requirements.txt

# from OS_CBP/TEAM13
pip install -r requirements.txt
```

**2. Generate Mock Data**
Seed the `data/` directory with realistic mock records:
```bash
# from OS_CBP (workspace root)
python TEAM13/utils/generate_mock_data.py

# from OS_CBP/TEAM13
python utils/generate_mock_data.py
```

---

## 🚀 Running the Services

### 1. Launch the Analytics Dashboard
The interactive dashboard provides data visualisation, filtering, and report downloads.
```bash
# recommended (works even if streamlit.exe launcher is stale)
# from OS_CBP (workspace root)
python -m streamlit run TEAM13/dashboard/app.py

# from OS_CBP/TEAM13
python -m streamlit run dashboard/app.py
```
*Opens automatically at `http://localhost:8501`*

### 2. Launch the Mock API
The FastAPI backend serves the mock data, simulating how external teams will push/pull data.
```bash
# from OS_CBP (workspace root)
uvicorn TEAM13.api.api:app --reload

# from OS_CBP/TEAM13
uvicorn api.api:app --reload
```
*Swagger UI available at: `http://127.0.0.1:8000/docs`*

---

## 📊 Overview of Features
*   **Time Series Analysis**: Track violations daily and monthly.
*   **Hotspot Analysis**: Rank campus zones by frequency and severity of overspeeding.
*   **Revenue Tracking**: Visualise paid vs. unpaid fine statuses and total collections.
*   **Repeat Offenders**: Automatically identify vehicles frequently violating rules.
*   **Live Export**: Export filtered `CSV` tables and `TXT` summary reports directly from the dashboard sidebar.
