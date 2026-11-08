"""The operator-facing sensor table must reflect evaluated measurements."""
import pandas as pd

from turbinehealth.monitor import HealthMonitor, DEFAULT_THRESHOLDS


def test_sensor_table_has_one_row_per_sensor_and_correct_units():
    sample = pd.DataFrame([{
        "timestamp": "2026-09-01T00:00:00Z",
        "turbine_id": "WT-SYNTHETIC",
        "wind_speed_mps": 10.0,
        "rotor_speed_rpm": 15.0,
        "generator_temp_c": 75.0,
        "gearbox_temp_c": 80.0,
        "oil_temp_c": 70.0,
        "vibration_mm_s": 2.0,
        "power_output_kw": 1800.0,
        "blade_pitch_deg": 4.0,
        "generator_rpm": 1500.0,
    }])
    monitor = HealthMonitor()
    evaluated = monitor.evaluate(sample)
    display = monitor.sensor_table(evaluated.iloc[0])

    assert len(display) == len(DEFAULT_THRESHOLDS)
    assert set(display["Sensor"]) == {
        name.replace("_", " ") for name in DEFAULT_THRESHOLDS
    }
    generator = display.loc[display["Sensor"].eq("generator temp c")].iloc[0]
    assert generator["Reading"] == 75
    assert generator["Unit"] == "°C"
    assert generator["Status"] == "HEALTHY"
