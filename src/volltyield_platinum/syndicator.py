from typing import Dict, List, Any, Optional

def anonymize_for_export(passport_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strips PII from passport data while retaining fields for analysis.

    STRIP: vin, driver_name, exact_gps
    KEEP: make, model, battery_chemistry, zip_code, soh, charge_patterns,
          thermal_events, fast_charge_ratio, kwh_drawn, hour_of_day
    """
    sensitive_fields = {"vin", "driver_name", "exact_gps"}

    anonymized = {
        k: v for k, v in passport_data.items()
        if k not in sensitive_fields
    }

    return anonymized

def calculate_actuarial_risk(anonymized_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Calculates risk score based on battery health data.

    Logic:
    - If average_soh > 95% AND thermal_events == 0: LOW_RISK / ELIGIBLE
    - If fast_charge_ratio > 80%: HIGH_RISK / INELIGIBLE
    - Else: STANDARD_RISK / ELIGIBLE (Default)
    """
    soh = anonymized_data.get("soh", 0.0)
    thermal_events = anonymized_data.get("thermal_events", 0)
    fast_charge_ratio = anonymized_data.get("fast_charge_ratio", 0.0)

    # Check High Risk first? Or Low Risk?
    # The prompt gives two conditions.
    # If fast_charge_ratio > 80%, it's HIGH_RISK.
    # If soh > 95 and thermal == 0, it's LOW_RISK.
    # What if both? High abuse but high SOH?
    # Usually "Abuse" implies high risk regardless of current SOH state in insurance.
    # However, standard Python if/elif/else structure means order matters.
    # I will prioritize High Risk detection as it is an exclusion criteria.

    if fast_charge_ratio > 0.80:
        return {"risk_cohort": "HIGH_RISK", "premium_discount": "INELIGIBLE"}

    if soh > 95.0 and thermal_events == 0:
        return {"risk_cohort": "LOW_RISK", "premium_discount": "ELIGIBLE"}

    return {"risk_cohort": "STANDARD_RISK", "premium_discount": "ELIGIBLE"}

def aggregate_grid_utilization(data_list: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Aggregates kwh_drawn by zip_code + hour_of_day.

    Returns a dictionary with keys "zip_code:hour" and values being total kwh.
    """
    aggregation = {}

    for entry in data_list:
        zip_code = entry.get("zip_code")
        hour = entry.get("hour_of_day")
        kwh = entry.get("kwh_drawn", 0.0)

        if zip_code is not None and hour is not None:
            key = f"{zip_code}:{hour}"
            aggregation[key] = aggregation.get(key, 0.0) + kwh

    return aggregation
