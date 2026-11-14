"""Two differently formatted timestamps for one instant are duplicates."""
import pandas as pd
import pytest

from turbinehealth.monitor import HealthMonitor


def record(timestamp, turbine_id="WT-SYNTHETIC"):
    return {
        "timestamp": timestamp,
        "turbine_id": turbine_id,
        "wind_speed_mps": 10,
        "rotor_speed_rpm": 15,
        "generator_temp_c": 75,
        "gearbox_temp_c": 80,
        "oil_temp_c": 70,
        "vibration_mm_s": 2,
        "power_output_kw": 1800,
        "blade_pitch_deg": 4,
        "generator_rpm": 1500,
    }


def test_equivalent_offsets_are_rejected_as_duplicate():
    frame = pd.DataFrame([
        record("2026-11-14T10:00:00Z"),
        record("2026-11-14T15:30:00+05:30"),
    ])
    with pytest.raises(ValueError, match="Duplicate turbine/timestamp"):
        HealthMonitor().evaluate(frame)


def test_same_instant_for_two_turbines_is_valid():
    frame = pd.DataFrame([
        record("2026-11-14T10:00:00Z", "WT-A"),
        record("2026-11-14T15:30:00+05:30", "WT-B"),
    ])
    evaluated = HealthMonitor().evaluate(frame)
    assert evaluated.health.tolist() == ["HEALTHY", "HEALTHY"]
    assert set(evaluated.turbine_id) == {"WT-A", "WT-B"}
