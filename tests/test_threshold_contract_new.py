from dataclasses import FrozenInstanceError

import pytest

from turbinehealth.monitor import DEFAULT_THRESHOLDS, Threshold


def test_threshold_objects_are_immutable():
    threshold = DEFAULT_THRESHOLDS["generator_temp_c"]
    with pytest.raises(FrozenInstanceError):
        threshold.healthy_max = 999


@pytest.mark.parametrize("sensor", list(DEFAULT_THRESHOLDS))
def test_healthy_values_remain_inside_warning_envelopes(sensor):
    rule = DEFAULT_THRESHOLDS[sensor]
    assert rule.valid_min <= rule.warning_min <= rule.healthy_min
    assert rule.healthy_max <= rule.warning_max <= rule.valid_max


def test_bad_nested_thresholds_are_rejected():
    with pytest.raises(ValueError):
        Threshold("C", 0, 10, 20, 60, 50, 100)
