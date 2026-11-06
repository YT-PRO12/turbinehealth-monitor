"""Latest state is per turbine, never just the last global row."""
import pandas as pd

from turbinehealth.monitor import latest_health


def test_latest_health_uses_each_turbines_latest_record():
    result = pd.DataFrame([
        {"timestamp": pd.Timestamp("2026-09-01T00:00:00Z"),
         "turbine_id": "WT-A", "health": "HEALTHY"},
        {"timestamp": pd.Timestamp("2026-09-01T00:02:00Z"),
         "turbine_id": "WT-B", "health": "WARNING"},
        {"timestamp": pd.Timestamp("2026-09-01T00:04:00Z"),
         "turbine_id": "WT-A", "health": "CRITICAL"},
    ])
    selected = latest_health(result).set_index("turbine_id")
    assert len(selected) == 2
    assert selected.loc["WT-A", "health"] == "CRITICAL"
    assert selected.loc["WT-B", "health"] == "WARNING"
