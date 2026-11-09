"""Alert history is not deduplicated or misrepresented as a forecast."""
import pandas as pd

from turbinehealth.monitor import HealthMonitor, recent_alerts


def sample(timestamp, temperature):
    return {
        "timestamp": timestamp,
        "turbine_id": "WT-SYNTHETIC",
        "wind_speed_mps": 10,
        "rotor_speed_rpm": 15,
        "generator_temp_c": temperature,
        "gearbox_temp_c": 80,
        "oil_temp_c": 70,
        "vibration_mm_s": 2,
        "power_output_kw": 1800,
        "blade_pitch_deg": 4,
        "generator_rpm": 1500,
    }


def test_repeated_abnormal_records_remain_separate_alerts():
    rows = pd.DataFrame([
        sample("2026-11-09T00:00:00Z", 75),
        sample("2026-11-09T00:05:00Z", 90),
        sample("2026-11-09T00:10:00Z", 110),
    ])
    evaluated = HealthMonitor().evaluate(rows)
    alerts = recent_alerts(evaluated)

    assert alerts["health"].tolist() == ["CRITICAL", "WARNING"]
    assert list(alerts["timestamp"]) == sorted(alerts["timestamp"], reverse=True)
    assert len(recent_alerts(evaluated, limit=1)) == 1
    assert len(evaluated) == 3
