import pandas as pd
from datetime import datetime

def export_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def generate_summary_report_text(violations: pd.DataFrame, top_zones: pd.DataFrame, repeat_offenders: pd.DataFrame, total_revenue: float) -> bytes:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_vio = len(violations)
    avg_speed = violations["overspeed_delta_kmph"].mean() if not violations.empty else 0.0
    
    lines = [
        "=== TEAM 13 ANALYTICS SUMMARY ===",
        f"Generated: {now}",
        f"Records  : {total_vio} violations",
        f"Revenue  : INR {total_revenue:,.2f}",
        f"Avg Overspd: {avg_speed:.2f} km/h",
        "\n--- TOP ZONES ---"
    ]
    if not top_zones.empty:
        for _, row in top_zones.head(5).iterrows():
            lines.append(f"- {row['zone_name']} ({row['total_violations']} vios)")
    
    lines.append("\n--- TOP OFFENDERS ---")
    if not repeat_offenders.empty:
        for _, row in repeat_offenders.head(5).iterrows():
            lines.append(f"- {row['vehicle_id']} ({row['total_violations']} vios)")
    
    return "\n".join(lines).encode("utf-8")
