"""Deterministic operational health monitoring; no prediction or ML."""
from dataclasses import dataclass
from math import isfinite
from numbers import Real
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Threshold:
    unit: str
    valid_min: float
    warning_min: float
    healthy_min: float
    healthy_max: float
    warning_max: float
    valid_max: float

    def __post_init__(self):
        values = [self.valid_min, self.warning_min, self.healthy_min, self.healthy_max, self.warning_max, self.valid_max]
        if any(isinstance(x, bool) or not isinstance(x, Real) or not isfinite(x) for x in values):
            raise ValueError("Thresholds must be finite numbers")
        if values != sorted(values):
            raise ValueError("Threshold ranges must be nested in ascending order")

    def classify(self, value):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real) or not isfinite(value):
            return "CRITICAL", "missing or non-finite reading"
        if not self.valid_min <= value <= self.valid_max:
            return "CRITICAL", "outside plausible demonstration range"
        if self.healthy_min <= value <= self.healthy_max:
            return "HEALTHY", "within healthy range"
        if self.warning_min <= value <= self.warning_max:
            return "WARNING", "outside healthy range"
        return "CRITICAL", "outside warning range"

DEFAULT_THRESHOLDS = {
    "wind_speed_mps": Threshold("m/s", 0, 0, 0, 20, 25, 60),
    "rotor_speed_rpm": Threshold("RPM", 0, 0, 0, 18, 22, 40),
    "generator_temp_c": Threshold("°C", -40, -20, 0, 80, 100, 180),
    "gearbox_temp_c": Threshold("°C", -40, -20, 0, 85, 100, 180),
    "oil_temp_c": Threshold("°C", -40, -20, 0, 80, 95, 180),
    "vibration_mm_s": Threshold("mm/s", 0, 0, 0, 2.8, 4.5, 30),
    "power_output_kw": Threshold("kW", 0, 0, 0, 2000, 2200, 3000),
    "blade_pitch_deg": Threshold("deg", 0, 0, 0, 85, 90, 90),
    "generator_rpm": Threshold("RPM", 0, 0, 0, 1800, 2000, 3000),
}
COLUMNS = ["timestamp", "turbine_id", *DEFAULT_THRESHOLDS]
SEVERITY = {"HEALTHY": 0, "WARNING": 1, "CRITICAL": 2}

def load_csv(source):
    try:
        frame = pd.read_csv(source, nrows=20001)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeError) as exc:
        raise ValueError("CSV must be a readable UTF-8 table with a header") from exc
    return frame

class HealthMonitor:
    def __init__(self, thresholds=None):
        self.thresholds = dict(DEFAULT_THRESHOLDS if thresholds is None else thresholds)
        if set(self.thresholds) != set(DEFAULT_THRESHOLDS):
            raise ValueError("Configure every documented sensor threshold")
        if not all(isinstance(x, Threshold) for x in self.thresholds.values()):
            raise ValueError("Every configured rule must be a Threshold")

    def evaluate(self, frame):
        missing = set(COLUMNS) - set(frame.columns)
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        if frame.columns.duplicated().any():
            raise ValueError("Duplicate column names are not allowed")
        if frame.empty or len(frame) > 20000:
            raise ValueError("Provide between 1 and 20,000 sensor records")
        result = frame[COLUMNS].copy().reset_index(drop=True)
        result["timestamp"] = pd.to_datetime(result.timestamp, errors="coerce", utc=True, format="ISO8601")
        if result.timestamp.isna().any():
            raise ValueError("Every record needs a valid ISO 8601 timestamp")
        result["turbine_id"] = result.turbine_id.astype("string").str.strip()
        if result.turbine_id.isna().any() or result.turbine_id.eq("").any():
            raise ValueError("Every record needs a turbine ID")
        if result.duplicated(["turbine_id", "timestamp"]).any():
            raise ValueError("Duplicate turbine/timestamp records are ambiguous")
        reasons = [[] for _ in range(len(result))]
        ranks = np.zeros(len(result), dtype=int)
        for column, rule in self.thresholds.items():
            numeric = pd.to_numeric(result[column], errors="coerce")
            booleans = result[column].map(lambda x: isinstance(x, (bool, np.bool_)))
            result[column] = numeric.astype(float).mask(booleans)
            readings = [rule.classify(value) for value in result[column]]
            result[f"{column}_status"] = [status for status, reason in readings]
            for idx, (status, reason) in enumerate(readings):
                ranks[idx] = max(ranks[idx], SEVERITY[status])
                if status != "HEALTHY":
                    reasons[idx].append(f"{column}: {reason}")
        result["health"] = np.array(["HEALTHY", "WARNING", "CRITICAL"])[ranks]
        result["reasons"] = ["; ".join(items) if items else "All readings within healthy ranges" for items in reasons]
        return result.sort_values(["timestamp", "turbine_id"]).reset_index(drop=True)

    def sensor_table(self, record):
        return pd.DataFrame([{"Sensor": col.replace("_", " "), "Reading": record[col], "Unit": rule.unit,
                              "Status": record[f"{col}_status"], "Healthy range": f"{rule.healthy_min}–{rule.healthy_max}"}
                             for col, rule in self.thresholds.items()])

def latest_health(result):
    """Latest recorded reading per turbine; not a live or freshness assessment."""
    return result.sort_values("timestamp").groupby("turbine_id", as_index=False).tail(1)

def recent_alerts(result, limit=20):
    """One alert per non-healthy record; repeated conditions stay visible."""
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be a positive integer")
    return result[result.health.ne("HEALTHY")].sort_values("timestamp", ascending=False).head(limit)[["timestamp", "turbine_id", "health", "reasons"]]

def thresholds_table(thresholds):
    return pd.DataFrame([{"Sensor": col, "Unit": rule.unit,
                          "Healthy (inclusive)": f"{rule.healthy_min} to {rule.healthy_max}",
                          "Warning envelope (inclusive)": f"{rule.warning_min} to {rule.warning_max}",
                          "Plausible envelope": f"{rule.valid_min} to {rule.valid_max}"}
                         for col, rule in thresholds.items()])
