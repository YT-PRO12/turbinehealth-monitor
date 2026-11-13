"""Per-monitor threshold overrides must not affect other monitor instances."""
import pandas as pd
import pytest

from turbinehealth.monitor import DEFAULT_THRESHOLDS, HealthMonitor, Threshold


def sample():
    return pd.DataFrame([{
        "timestamp": "2026-11-13T09:00:00Z",
        "turbine_id": "WT-SYNTH",
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


def test_custom_rule_changes_only_its_monitor():
    modified = dict(DEFAULT_THRESHOLDS)
    modified["generator_temp_c"] = Threshold("°C", -40, -20, 0, 60, 80, 180)
    custom = HealthMonitor(modified).evaluate(sample())
    original = HealthMonitor().evaluate(sample())
    assert custom.loc[0, "generator_temp_c_status"] == "WARNING"
    assert original.loc[0, "generator_temp_c_status"] == "HEALTHY"
    assert DEFAULT_THRESHOLDS["generator_temp_c"].healthy_max == 80


def test_partial_threshold_mapping_is_rejected():
    with pytest.raises(ValueError, match="every documented sensor"):
        HealthMonitor({"generator_temp_c": DEFAULT_THRESHOLDS["generator_temp_c"]})
