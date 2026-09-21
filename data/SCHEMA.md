# Sensor CSV and threshold contract

UTF-8 CSV, ISO 8601 timestamps (UTC when an offset is absent), nonblank `turbine_id`.
One row per turbine/timestamp; duplicates reject the dataset. Maximum 20,000 rows
and 5 MB per upload. All nine sensor columns below are required; extra columns ignored.

| Sensor column | Unit | Healthy, inclusive | Warning envelope, inclusive | Plausible envelope |
|---|---|---|---|---|
| wind_speed_mps | m/s | 0–20 | 0–25 | 0–60 |
| rotor_speed_rpm | RPM | 0–18 | 0–22 | 0–40 |
| generator_temp_c | °C | 0–80 | −20–100 | −40–180 |
| gearbox_temp_c | °C | 0–85 | −20–100 | −40–180 |
| oil_temp_c | °C | 0–80 | −20–95 | −40–180 |
| vibration_mm_s | mm/s | 0–2.8 | 0–4.5 | 0–30 |
| power_output_kw | kW | 0–2000 | 0–2200 | 0–3000 |
| blade_pitch_deg | degrees | 0–85 | 0–90 | 0–90 |
| generator_rpm | RPM | 0–1800 | 0–2000 | 0–3000 |

All limits are generic demonstration assumptions, not manufacturer specifications.
WARNING means outside healthy but inside the warning envelope. Outside warning is
CRITICAL. Outside plausible is CRITICAL with a data-range reason. Non-finite or
non-numeric values are CRITICAL data-quality alerts.

The sample generator uses a fixed seed. WT-002 has an injected late gearbox
temperature rise; WT-003 has rising generator temperature and vibration. There is
no personal, proprietary or manufacturer telemetry in this fixture.
