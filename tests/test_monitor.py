from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from turbinehealth.monitor import (Threshold, HealthMonitor, DEFAULT_THRESHOLDS,
    latest_health, recent_alerts, load_csv, thresholds_table)

@pytest.fixture
def row():
    return pd.DataFrame([{"timestamp":"2026-09-01T00:00:00Z","turbine_id":"WT-001",
        "wind_speed_mps":10.,"rotor_speed_rpm":15.,"generator_temp_c":75.,
        "gearbox_temp_c":80.,"oil_temp_c":70.,"vibration_mm_s":2.,
        "power_output_kw":1800.,"blade_pitch_deg":4.,"generator_rpm":1500.}])

@pytest.mark.parametrize("value,state", [(80,"HEALTHY"),(80.001,"WARNING"),(100,"WARNING"),
    (100.001,"CRITICAL"),(0,"HEALTHY"),(-.001,"WARNING"),(-20,"WARNING"),
    (-20.001,"CRITICAL"),(-41,"CRITICAL"),(181,"CRITICAL"),
    (np.nan,"CRITICAL"),(np.inf,"CRITICAL"),(True,"CRITICAL"),("80","CRITICAL")])
def test_temperature_boundaries(value,state):
    assert DEFAULT_THRESHOLDS["generator_temp_c"].classify(value)[0] == state

@pytest.mark.parametrize("sensor", list(DEFAULT_THRESHOLDS))
def test_every_sensor_healthy_and_warning_boundary(sensor):
    rule = DEFAULT_THRESHOLDS[sensor]
    assert rule.classify(rule.healthy_min)[0] == "HEALTHY"
    assert rule.classify(rule.healthy_max)[0] == "HEALTHY"
    assert rule.classify(rule.warning_max)[0] == ("WARNING" if rule.warning_max > rule.healthy_max else "HEALTHY")

def test_overall_worst_sensor(row):
    row.loc[0,"gearbox_temp_c"] = 92
    monitor = HealthMonitor()
    result = monitor.evaluate(row)
    assert result.health.iloc[0] == "WARNING"
    assert "gearbox_temp_c" in result.reasons.iloc[0]
    row.loc[0,"vibration_mm_s"] = 4.6
    result = monitor.evaluate(row)
    assert result.health.iloc[0] == "CRITICAL"
    assert len(monitor.sensor_table(result.iloc[0])) == 9

def test_missing_sensor_is_not_healthy(row):
    row.loc[0,"oil_temp_c"] = np.nan
    result = HealthMonitor().evaluate(row)
    assert result.health.iloc[0] == "CRITICAL"
    assert "missing or non-finite" in result.reasons.iloc[0]

def test_newest_record_and_alert_order(row):
    other = row.copy()
    other.loc[0,"timestamp"] = "2026-09-01T00:10:00Z"
    other.loc[0,"gearbox_temp_c"] = 110
    result = HealthMonitor().evaluate(pd.concat([other,row],ignore_index=True))
    assert latest_health(result).health.iloc[0] == "CRITICAL"
    assert recent_alerts(result).health.tolist() == ["CRITICAL"]
    assert recent_alerts(HealthMonitor().evaluate(row)).empty
    with pytest.raises(ValueError):
        recent_alerts(result, 0)

@pytest.mark.parametrize("column,value,reason", [("timestamp","bad","timestamp"),("turbine_id"," ","turbine ID")])
def test_invalid_identifiers(row,column,value,reason):
    row.loc[0,column] = value
    with pytest.raises(ValueError,match=reason):
        HealthMonitor().evaluate(row)

def test_schema_duplicates_empty(row):
    monitor = HealthMonitor()
    for bad in [row.drop(columns="generator_rpm"), row.iloc[:0], pd.concat([row,row]),
                pd.concat([row,row[["timestamp"]]],axis=1)]:
        with pytest.raises(ValueError):
            monitor.evaluate(bad)

def test_configurable_thresholds(row):
    from dataclasses import replace
    rules = dict(DEFAULT_THRESHOLDS)
    rules["generator_temp_c"] = replace(rules["generator_temp_c"], healthy_max=70)
    assert HealthMonitor(rules).evaluate(row).health.iloc[0] == "WARNING"
    assert len(thresholds_table(rules)) == 9
    with pytest.raises(ValueError):
        HealthMonitor({})
    with pytest.raises(ValueError):
        Threshold("C",0,0,0,100,90,180)
    with pytest.raises(ValueError):
        Threshold("C",0,0,0,80,float("nan"),180)

def test_sample_fleet_has_all_three_states():
    source = Path(__file__).parents[1] / "data/turbine_sensor_samples.csv"
    result = HealthMonitor().evaluate(load_csv(source))
    assert set(latest_health(result).health) == {"HEALTHY","WARNING","CRITICAL"}
    assert len(latest_health(result)) == 3
