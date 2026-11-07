import numpy as np
import pytest

from turbinehealth.monitor import DEFAULT_THRESHOLDS, Threshold


def test_thresholds_enforce_valid_order():
    with pytest.raises(ValueError):
        Threshold("C", 0, 10, 20, 60, 50, 100)


@pytest.mark.parametrize("bad", [None, float("nan"), np.inf, True, "75"])
def test_missing_or_non_numeric_values_are_critical(bad):
    status, reason = DEFAULT_THRESHOLDS["generator_temp_c"].classify(bad)
    assert status == "CRITICAL"
    assert "missing or non-finite" in reason


def test_healthy_boundaries_are_inclusive():
    rule = DEFAULT_THRESHOLDS["generator_temp_c"]
    assert rule.classify(rule.healthy_min)[0] == "HEALTHY"
    assert rule.classify(rule.healthy_max)[0] == "HEALTHY"
    assert rule.classify(rule.warning_max)[0] == "WARNING"
