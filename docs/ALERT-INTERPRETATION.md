# Interpreting health alerts

The dashboard classifies **historical synthetic** measurements using configured ranges; it is not a live monitoring platform or failure predictor.

- HEALTHY: inside the inclusive healthy range.
- WARNING: outside healthy but within the warning envelope.
- CRITICAL: outside warning or plausibility limits, or missing/non-finite values.
- Overall turbine status is the worst sensor status for that recorded row.

A CRITICAL data-quality alarm may indicate a broken or missing sensor reading, not a confirmed machine fault. Repeated abnormal records generate repeated alerts.

The most recent recorded timestamp does not establish current telemetry freshness. Real operations require freshness monitoring, verified device identity, domain-specific threshold calibration, and human response procedures.

See [schema](../data/SCHEMA.md) and [monitor tests](../tests/test_monitor.py).
