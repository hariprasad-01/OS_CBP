"""Analytics Dashboard"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from analytics.analytics import top_overspeeding_zones, repeat_offenders, violations_over_time, peak_hours_analysis, fine_statistics, department_analysis, vehicle_history
from utils.report_utils import export_to_csv, generate_summary_report_text

st.set_page_config(page_title="Dashboard", layout="wide")

@st.cache_data
def get_data():
    return load_data()

frames = get_data()
required_frames = ["vehicles", "violations", "fines", "locations"]
if not frames or any(frames.get(name) is None for name in required_frames):
    st.error("Missing or invalid data schema. Regenerate mock data first.")
    st.stop()

if frames.get("violations").empty:
    st.error("Missing data. Generate mock data first.")
    st.stop()

vehicles, violations, fines, locations = frames["vehicles"], frames["violations"], frames["fines"], frames["locations"]

st.sidebar.title("Filters")
date_range = st.sidebar.date_input("Date Range", value=(pd.to_datetime(violations["date"]).min().date(), pd.to_datetime(violations["date"]).max().date()))
if len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
else:
    start_date = end_date = date_range[0]

# Additional Filters
departments = ["All"] + sorted(vehicles["department"].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)

zones = ["All"] + sorted(locations["zone_name"].dropna().unique().tolist())
selected_zone = st.sidebar.selectbox("Location / Zone", zones)

# Apply Filters
violations["date_dt"] = pd.to_datetime(violations["date"]).dt.date
mask = (violations["date_dt"] >= start_date) & (violations["date_dt"] <= end_date)
if selected_dept != "All":
    # Get vehicles for that department
    dept_vehicles = vehicles[vehicles["department"] == selected_dept]["vehicle_id"].unique()
    mask = mask & (violations["vehicle_id"].isin(dept_vehicles))

if selected_zone != "All":
    # Get zone_id for that zone_name
    zone_matches = locations[locations["zone_name"] == selected_zone]["zone_id"].values
    if len(zone_matches) == 0:
        st.warning("Selected zone not found in location data.")
        st.stop()
    zone_id = zone_matches[0]
    mask = mask & (violations["zone_id"] == zone_id)

f_violations = violations[mask]
f_fines = fines[fines["violation_id"].isin(f_violations["violation_id"])] if fines is not None else pd.DataFrame()

# Export Logic
st.sidebar.divider()
st.sidebar.subheader("Export & Reports")
if not f_violations.empty:
    st.sidebar.download_button("Download CSV", export_to_csv(f_violations), "violations_filtered.csv", "text/csv")
    re_bytes = generate_summary_report_text(f_violations, top_overspeeding_zones(f_violations, locations, 5), repeat_offenders(f_violations, vehicles, 1, 5), fine_statistics(f_fines).get("total_amount_collected", 0))
    st.sidebar.download_button("Download Report TXT", re_bytes, "report.txt", "text/plain")

st.title("Traffic Analytics Dashboard")

if f_violations.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Dashboard Overview", "Data Tables", "Vehicle History"])

with tab1:
    stats = fine_statistics(f_fines)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Violations", len(f_violations))
    col2.metric("Total Fines Generated", stats.get('total_fines', 0))
    col3.metric("Paid Revenue (INR)", f"₹{stats.get('total_amount_collected',0):,.0f}")
    col4.metric("Pending Revenue (INR)", f"₹{stats.get('pending_amount',0):,.0f}")
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1: 
        trend_fig = px.line(violations_over_time(f_violations), x="period", y="total_violations", title="Violations Trend Over Time", markers=True)
        trend_fig.update_xaxes(range=[str(start_date), str(end_date)])
        st.plotly_chart(trend_fig, use_container_width=True)
    with c2: 
        st.plotly_chart(px.bar(top_overspeeding_zones(f_violations, locations), x="zone_name", y="total_violations", title="Top Overspeeding Zones", color="total_violations", color_continuous_scale="Reds"), use_container_width=True)
        
    st.divider()
    c3, c4 = st.columns(2)
    with c3:
        dept_data = department_analysis(f_violations, vehicles)
        st.plotly_chart(px.bar(dept_data, x="department", y="total_violations", title="Violations by Department", color="department"), use_container_width=True)
    with c4:
        offenders_data = repeat_offenders(f_violations, vehicles, min_violations=1)
        st.plotly_chart(px.bar(offenders_data.head(10), x="vehicle_id", y="total_violations", hover_data=["owner_name"], title="Top Repeat Offenders"), use_container_width=True)

    st.divider()
    st.plotly_chart(px.bar(peak_hours_analysis(f_violations), x="hour", y="total_violations", color="time_of_day", title="Peak Violation Hours"), use_container_width=True)

with tab2:
    st.subheader("Repeat Offenders (Violation Frequencies)")
    offenders = repeat_offenders(f_violations, vehicles, min_violations=1, top_n=500)
    st.dataframe(offenders, use_container_width=True)
    
    st.subheader("Violation Records")
    st.dataframe(f_violations.merge(locations[["zone_id", "zone_name"]], on="zone_id", how="left").merge(vehicles[["vehicle_id", "owner_name", "department", "id_number", "phone_number"]], on="vehicle_id", how="left"), use_container_width=True)
    
    st.subheader("Fine Records")
    st.dataframe(f_fines, use_container_width=True)

with tab3:
    st.subheader("Vehicle-Level Lookup")
    all_vehicles = vehicles["vehicle_id"].unique().tolist()
    search_vid = st.selectbox("Select or Type Vehicle ID to search:", [""] + all_vehicles)
    
    if search_vid:
        vh = vehicle_history(f_violations, f_fines, search_vid)
        
        v_info = vehicles[vehicles["vehicle_id"] == search_vid].iloc[0]
        st.markdown(f"**Owner:** {v_info['owner_name']} | **ID:** {v_info.get('id_number', 'N/A')} | **Role:** {v_info['owner_type']} | **Dept:** {v_info['department']} | **Phone:** {v_info.get('phone_number', 'N/A')}")
        
        summary = vh["summary"]
        vc1, vc2, vc3 = st.columns(3)
        vc1.metric("Total Violations", summary.get("total_violations", 0))
        vc2.metric("Paid Fines", summary.get("total_fines_paid", 0))
        vc3.metric("Pending Fines", summary.get("total_fines_pending", 0))
        
        st.markdown("#### Violation & Fine Timeline")
        st.dataframe(vh["history"], use_container_width=True)
