import pytest
from voltyield_ledger_core.regulatory import RegulatoryEngine

def test_carbon_rail_jurisdictions():
    engine = RegulatoryEngine(rulepack_version="test")

    # Test CA (15 cents/kWh)
    # Input 1000 Wh (1 kWh) -> 15 cents
    res_ca = engine.evaluate_us_lcfs(1000, "CA", True, True)
    assert res_ca.eligible is True
    assert res_ca.amount == 15
    assert res_ca.trace["rate_cents_per_kwh"] == 15
    assert res_ca.citation == "Cal. Code Regs. Tit. 17 § 95481"

    # Test OR (12 cents/kWh)
    res_or = engine.evaluate_us_lcfs(1000, "OR", True, True)
    assert res_or.eligible is True
    assert res_or.amount == 12
    assert res_or.trace["rate_cents_per_kwh"] == 12

    # Test WA (14 cents/kWh)
    res_wa = engine.evaluate_us_lcfs(1000, "WA", True, True)
    assert res_wa.eligible is True
    assert res_wa.amount == 14
    assert res_wa.trace["rate_cents_per_kwh"] == 14

def test_carbon_rail_evidence_requirements():
    engine = RegulatoryEngine(rulepack_version="test")

    # Missing ANSI Meter
    res_no_meter = engine.evaluate_us_lcfs(1000, "CA", False, True)
    assert res_no_meter.eligible is False
    assert res_no_meter.amount == 0
    assert res_no_meter.trace["reason"] == "Invalid Jurisdiction or Evidence"

    # Missing GPS Lock
    res_no_gps = engine.evaluate_us_lcfs(1000, "CA", True, False)
    assert res_no_gps.eligible is False
    assert res_no_gps.amount == 0
    assert res_no_gps.trace["reason"] == "Invalid Jurisdiction or Evidence"

    # Missing Both
    res_none = engine.evaluate_us_lcfs(1000, "CA", False, False)
    assert res_none.eligible is False

def test_carbon_rail_invalid_jurisdiction():
    engine = RegulatoryEngine(rulepack_version="test")

    res_ny = engine.evaluate_us_lcfs(1000, "NY", True, True)
    assert res_ny.eligible is False
    assert res_ny.amount == 0
    assert res_ny.trace["reason"] == "Invalid Jurisdiction or Evidence"

def test_carbon_rail_math_units():
    engine = RegulatoryEngine(rulepack_version="test")

    # Test large input to verify no overflow/weirdness and confirm linear scaling
    # 1 MWh = 1,000,000 Wh -> 1,000 kWh
    # CA Rate: 15 cents/kWh
    # Expected: 15 * 1,000 = 15,000 cents ($150)
    res = engine.evaluate_us_lcfs(1000000, "CA", True, True)
    assert res.amount == 15000

    # Test fractional result truncation (integer arithmetic)
    # 500 Wh (0.5 kWh) -> 0.5 * 15 = 7.5 cents -> 7 cents (floor)
    # Code: (500 * 15) // 1000 = 7500 // 1000 = 7
    res_small = engine.evaluate_us_lcfs(500, "CA", True, True)
    assert res_small.amount == 7
