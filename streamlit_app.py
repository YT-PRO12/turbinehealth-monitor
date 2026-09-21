"""Operational health dashboard with transparent threshold rules."""
from pathlib import Path
from dataclasses import replace
import matplotlib.pyplot as plt
import streamlit as st
from turbinehealth.monitor import HealthMonitor, DEFAULT_THRESHOLDS, load_csv, latest_health, recent_alerts, thresholds_table
from turbinehealth.plots import trend_plot

st.set_page_config(page_title="TurbineHealth Monitor", page_icon="🌬️", layout="wide")
st.caption("ENGINEERING TOOLKIT / OPERATIONAL HEALTH")
st.title("TurbineHealth Monitor")
st.write("Explore turbine sensor readings, investigate alerts and inspect historical trends.")
st.info("Historical synthetic snapshot · demonstration thresholds · no failure prediction")
sample = Path(__file__).parent / "data/turbine_sensor_samples.csv"
with st.sidebar:
    st.header("Data and monitoring")
    upload = st.file_uploader("Upload turbine sensor CSV", type=["csv"])
    st.download_button("Download sample CSV", sample.read_bytes(), "turbine_sensor_samples.csv", "text/csv")
    st.caption("Uploads stay in session memory. Maximum 5 MB / 20,000 records.")
    st.subheader("Generator temperature limits")
    normal_max = st.slider("Healthy upper bound (°C)", 40, 100, 80)
    warning_max = st.slider("Warning upper bound (°C)", 80, 140, 100)
if warning_max < normal_max:
    st.error("Warning upper bound must be at least the healthy upper bound.")
    st.stop()
rules = dict(DEFAULT_THRESHOLDS)
rules["generator_temp_c"] = replace(rules["generator_temp_c"], healthy_max=normal_max, warning_max=warning_max)
monitor = HealthMonitor(rules)
try:
    result = monitor.evaluate(load_csv(upload if upload is not None else sample))
except (ValueError, OSError) as exc:
    st.error(str(exc))
    st.stop()
fleet = latest_health(result)
cols = st.columns(4)
cols[0].metric("Turbines", len(fleet))
for col, state in zip(cols[1:], ["HEALTHY", "WARNING", "CRITICAL"]):
    col.metric(state.title(), int(fleet.health.eq(state).sum()))
turbine = st.selectbox("Select turbine", sorted(result.turbine_id.unique()), key="turbine")
selected = result[result.turbine_id.eq(turbine)]
latest = selected.iloc[-1]
st.subheader(f'{turbine} · {latest["health"]}')
st.caption(f'Latest recorded sample: {latest["timestamp"]:%Y-%m-%d %H:%M UTC}. Status describes this historical record, not current equipment health.')
show = {"HEALTHY": st.success, "WARNING": st.warning, "CRITICAL": st.error}[latest["health"]]
show(latest["reasons"])
overview, alerts, config = st.tabs(["Sensors and trends", "Recent alerts", "Thresholds and method"])
with overview:
    st.dataframe(monitor.sensor_table(latest), use_container_width=True, hide_index=True)
    sensor = st.selectbox("Trend parameter", list(rules), index=2, format_func=lambda name: name.replace("_", " ").title())
    fig = trend_plot(selected, sensor, rules[sensor])
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
with alerts:
    st.caption("Most recent 20 non-healthy records for the selected turbine; repeated conditions are retained.")
    alert_frame = recent_alerts(selected)
    if alert_frame.empty:
        st.success("No alerts in the selected turbine history.")
    else:
        st.dataframe(alert_frame, use_container_width=True, hide_index=True)
    st.subheader("Fleet snapshot")
    st.dataframe(fleet[["turbine_id", "timestamp", "health", "reasons"]], use_container_width=True, hide_index=True)
with config:
    st.dataframe(thresholds_table(rules), use_container_width=True, hide_index=True)
    st.markdown("""**How classification works:** Healthy range → HEALTHY. Outside healthy but within the warning envelope → WARNING. Outside the warning envelope, invalid or missing sensor reading → CRITICAL.

Boundary values belong to the less severe range. The worst sensor state determines overall health. Invalid sensor values are data-quality alerts; they do not prove an equipment fault.

All limits are configurable examples for a generic demonstration turbine. They are not Siemens Gamesa specifications. This tool uses historical records and does not predict failures, model operating modes or assess data freshness.""")
