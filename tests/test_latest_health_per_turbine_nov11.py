"""Latest historical status must not be selected globally."""
import pandas as pd

from turbinehealth.monitor import latest_health


def test_latest_reading_is_selected_per_turbine_not_per_table():
    records = pd.DataFrame([
        {"timestamp": pd.Timestamp("2026-11-11T10:00:00Z"),
         "turbine_id": "WT-A", "health": "WARNING"},
        {"timestamp": pd.Timestamp("2026-11-11T10:05:00Z"),
         "turbine_id": "WT-B", "health": "CRITICAL"},
        {"timestamp": pd.Timestamp("2026-11-11T10:10:00Z"),
         "turbine_id": "WT-A", "health": "HEALTHY"},
    ])
    result = latest_health(records).set_index("turbine_id")
    assert len(result) == 2
    assert result.loc["WT-A", "health"] == "HEALTHY"
    assert result.loc["WT-B", "health"] == "CRITICAL"
