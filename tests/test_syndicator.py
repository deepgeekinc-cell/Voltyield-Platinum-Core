import pytest
from src.volltyield_platinum.syndicator import anonymize_for_export, calculate_actuarial_risk, aggregate_grid_utilization

def test_anonymize_for_export():
    raw_data = {
        "vin": "12345ABC",
        "driver_name": "John Doe",
        "exact_gps": "37.7749,-122.4194",
        "make": "Tesla",
        "model": "Model 3",
        "soh": 98.0,
        "zip_code": "94103"
    }

    result = anonymize_for_export(raw_data)

    assert "vin" not in result
    assert "driver_name" not in result
    assert "exact_gps" not in result
    assert result["make"] == "Tesla"
    assert result["soh"] == 98.0
    assert result["zip_code"] == "94103"

def test_risk_low():
    data = {"soh": 96.0, "thermal_events": 0, "fast_charge_ratio": 0.10}
    result = calculate_actuarial_risk(data)
    assert result == {"risk_cohort": "LOW_RISK", "premium_discount": "ELIGIBLE"}

def test_risk_high_abuse():
    # Fast charge ratio > 80%
    data = {"soh": 96.0, "thermal_events": 0, "fast_charge_ratio": 0.85}
    result = calculate_actuarial_risk(data)
    assert result == {"risk_cohort": "HIGH_RISK", "premium_discount": "INELIGIBLE"}

def test_risk_high_abuse_trumps_low_risk():
    # Even if SOH is high and no thermal events, abuse makes it high risk
    data = {"soh": 99.0, "thermal_events": 0, "fast_charge_ratio": 0.90}
    result = calculate_actuarial_risk(data)
    assert result == {"risk_cohort": "HIGH_RISK", "premium_discount": "INELIGIBLE"}

def test_risk_standard():
    # SOH not high enough for Low Risk, but not abusive enough for High Risk
    data = {"soh": 90.0, "thermal_events": 0, "fast_charge_ratio": 0.50}
    result = calculate_actuarial_risk(data)
    assert result == {"risk_cohort": "STANDARD_RISK", "premium_discount": "ELIGIBLE"}

    # Thermal event present (prevents Low Risk)
    data = {"soh": 98.0, "thermal_events": 1, "fast_charge_ratio": 0.10}
    result = calculate_actuarial_risk(data)
    assert result == {"risk_cohort": "STANDARD_RISK", "premium_discount": "ELIGIBLE"}

def test_grid_aggregation():
    data = [
        {"zip_code": "10001", "hour_of_day": 14, "kwh_drawn": 10.0},
        {"zip_code": "10001", "hour_of_day": 14, "kwh_drawn": 5.5},
        {"zip_code": "10001", "hour_of_day": 15, "kwh_drawn": 20.0},
        {"zip_code": "90210", "hour_of_day": 14, "kwh_drawn": 8.0},
    ]

    result = aggregate_grid_utilization(data)

    assert result["10001:14"] == 15.5
    assert result["10001:15"] == 20.0
    assert result["90210:14"] == 8.0
    assert len(result) == 3

def test_grid_aggregation_missing_data():
    data = [
        {"zip_code": "10001", "kwh_drawn": 10.0}, # Missing hour
        {"hour_of_day": 14, "kwh_drawn": 5.5},    # Missing zip
        {"zip_code": "10001", "hour_of_day": 14, "kwh_drawn": 10.0},
    ]

    result = aggregate_grid_utilization(data)

    # Should only count the valid entry
    assert result["10001:14"] == 10.0
    assert len(result) == 1
