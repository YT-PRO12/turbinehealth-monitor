"""Ambiguous turbine samples must not reach historical health summaries."""
import pandas as pd
import pytest

from turbinehealth.monitor import HealthMonitor


def row(turbine_id):
    return {
        "timestamp": "2026-11-12T10:00:00Z",
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


def test_duplicate_turbine_and_timestamp_is_rejected():
    with pytest.raises(ValueError, match="Duplicate turbine/timestamp"):
        HealthMonitor().evaluate(pd.DataFrame([row("WT-A"), row(" WT-A ")]))


@pytest.mark.parametrize("invalid_id", ["", "  ", None])
def test_missing_or_blank_turbine_id_is_rejected(invalid_id):
    with pytest.raises(ValueError, match="turbine ID"):
        HealthMonitor().evaluate(pd.DataFrame([row(invalid_id)]))
