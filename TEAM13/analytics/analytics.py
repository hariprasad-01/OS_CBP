"""Team 13 — Analytics Engine"""
import pandas as pd

def top_overspeeding_zones(violations: pd.DataFrame, locations: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    agg = violations.groupby("zone_id").agg(total_violations=("violation_id", "count"), avg_overspeed_delta_kmph=("overspeed_delta_kmph", "mean")).reset_index()
    return agg.merge(locations[["zone_id", "zone_name", "location_type"]], on="zone_id", how="left").sort_values("total_violations", ascending=False).head(top_n)

def repeat_offenders(violations: pd.DataFrame, vehicles: pd.DataFrame, min_violations: int = 2, top_n: int = 20) -> pd.DataFrame:
    agg = violations.groupby("vehicle_id").agg(total_violations=("violation_id", "count")).reset_index()
    agg = agg[agg["total_violations"] >= min_violations]
    return agg.merge(vehicles[["vehicle_id", "owner_name", "owner_type"]], on="vehicle_id", how="left").sort_values("total_violations", ascending=False).head(top_n)

def violations_over_time(violations: pd.DataFrame, freq: str = "daily") -> pd.DataFrame:
    if freq not in {"daily", "monthly"}:
        raise ValueError("freq must be either 'daily' or 'monthly'")

    vio = violations.copy()
    if not pd.api.types.is_datetime64_any_dtype(vio["timestamp"]): vio["timestamp"] = pd.to_datetime(vio["timestamp"], utc=True, errors="coerce")
    vio["period"] = vio["timestamp"].dt.date if freq == "daily" else vio["timestamp"].dt.to_period("M").astype(str)
    return vio.groupby("period").agg(total_violations=("violation_id", "count")).reset_index().sort_values("period")

def peak_hours_analysis(violations: pd.DataFrame) -> pd.DataFrame:
    vio = violations.copy()
    if not pd.api.types.is_datetime64_any_dtype(vio["timestamp"]): vio["timestamp"] = pd.to_datetime(vio["timestamp"], utc=True, errors="coerce")
    vio["hour"] = vio["timestamp"].dt.hour
    if "time_of_day" not in vio.columns:
        vio["time_of_day"] = "Unknown"
    res = vio.groupby(["hour", "time_of_day"]).agg(total_violations=("violation_id", "count")).reset_index().sort_values("hour")
    return res

def fine_statistics(fines: pd.DataFrame) -> dict:
    fin = fines.copy()
    paid_mask = fin["status"] == "Paid"
    pending_mask = fin["status"] == "Pending"
    total_col = fin.loc[paid_mask, "final_amount_inr"].sum() if "final_amount_inr" in fin.columns else 0.0
    pending_col = fin.loc[pending_mask, "amount_inr"].sum() if "amount_inr" in fin.columns else 0.0
    return {
        "total_fines": int(len(fin)), 
        "total_amount_collected": float(total_col),
        "paid_count": int(paid_mask.sum()),
        "pending_count": int(pending_mask.sum()),
        "pending_amount": float(pending_col)
    }

def department_analysis(violations: pd.DataFrame, vehicles: pd.DataFrame) -> pd.DataFrame:
    vio = violations.merge(vehicles[["vehicle_id", "department"]], on="vehicle_id", how="left")
    return vio.groupby("department").agg(total_violations=("violation_id", "count")).reset_index().sort_values("total_violations", ascending=False)

def vehicle_history(violations: pd.DataFrame, fines: pd.DataFrame, vehicle_id: str) -> dict:
    v_vio = violations[violations["vehicle_id"] == vehicle_id]
    v_fines = fines[fines["vehicle_id"] == vehicle_id] if fines is not None and not fines.empty else pd.DataFrame()
    
    if v_vio.empty: return {"history": pd.DataFrame(), "summary": {}}
    
    if not v_fines.empty:
        history = v_vio.merge(v_fines[["violation_id", "amount_inr", "status"]], on="violation_id", how="left", suffixes=("_vio", "_fine"))
        history.rename(columns={"status_vio": "violation_status", "status_fine": "fine_status"}, inplace=True)
    else:
        history = v_vio.copy()
        history["amount_inr"] = 0.0
        history["fine_status"] = "No Fine"
        history.rename(columns={"status": "violation_status"}, inplace=True)
        
    summary = {
        "total_violations": len(v_vio),
        "total_fines_paid": len(history[history["fine_status"] == "Paid"]) if "fine_status" in history.columns else 0,
        "total_fines_pending": len(history[history["fine_status"] == "Pending"]) if "fine_status" in history.columns else 0
    }
    return {"history": history.sort_values("timestamp", ascending=False), "summary": summary}
