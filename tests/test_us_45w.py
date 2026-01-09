import pytest
from volltyield_ledger_core.regulatory import RegulatoryEngine

@pytest.fixture
def engine():
    return RegulatoryEngine(rulepack_version="v1.0")

def test_us_45w_case_a_light_duty(engine):
    """
    Case A (Light Duty): 5,000 lbs vehicle, $40,000 price.
    Expect result ~ $6,000 (15%).
    $40,000 = 4,000,000 minor units.
    15% of 4,000,000 = 600,000 minor units ($6,000).
    Cap for < 14,000 lbs is $7,500 (750,000).
    Result should be 600,000.
    """
    result = engine.evaluate_us_45w(
        ref_date="2023-06-15",
        vehicle_weight_lbs=5000,
        sale_price_minor=4000000,
        is_tax_exempt_entity=False
    )

    assert result.eligible is True
    assert result.amount == 600000
    assert result.rule_id == "US_45W_2026"
    assert result.trace["vehicle_weight"] == 5000
    assert result.trace["cap_limit"] == 750000

def test_us_45w_case_b_heavy_duty(engine):
    """
    Case B (Heavy Duty): 20,000 lbs vehicle, $300,000 price.
    Expect result $40,000 (Cap hit).
    $300,000 = 30,000,000 minor units.
    15% of 30,000,000 = 4,500,000 ($45,000).
    Cap for >= 14,000 lbs is $40,000 (4,000,000).
    Result should be 4,000,000.
    """
    result = engine.evaluate_us_45w(
        ref_date="2023-06-15",
        vehicle_weight_lbs=20000,
        sale_price_minor=30000000,
        is_tax_exempt_entity=False
    )

    assert result.eligible is True
    assert result.amount == 4000000
    assert result.rule_id == "US_45W_2026"
    assert result.trace["vehicle_weight"] == 20000
    assert result.trace["cap_limit"] == 4000000

def test_us_45w_sunset_fail(engine):
    """Test date outside effective window."""
    result = engine.evaluate_us_45w(
        ref_date="2022-12-31",
        vehicle_weight_lbs=5000,
        sale_price_minor=4000000,
        is_tax_exempt_entity=False
    )
    assert result.eligible is False
    assert result.amount == 0
