"""The operator-facing sensor table must reflect evaluated measurements."""
from turbinehealth.monitor import HealthMonitor, DEFAULT_THRESHOLDS


def test_sensor_table_has_one_row_per_sensor_and_correct_units(row):
    monitor = HealthMonitor()
    evaluated = monitor.evaluate(row)
    display = monitor.sensor_table(evaluated.iloc[0])

    assert len(display) == len(DEFAULT_THRESHOLDS)
    assert set(display["Sensor"]) == {
        name.replace("_", " ") for name in DEFAULT_THRESHOLDS
    }
    generator = display.loc[display["Sensor"].eq("generator temp c")].iloc[0]
    assert generator["Reading"] == 75
    assert generator["Unit"] == "°C"
    assert generator["Status"] == "HEALTHY"
