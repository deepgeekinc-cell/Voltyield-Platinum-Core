import pytest
from voltyield_ledger_core.regulatory import RegulatoryEngine

def test_us_macrs_2026():
    engine = RegulatoryEngine("v1")

    # Test case 1: 2024 service date (60% bonus)
    # Cost: 10000 ($100.00)
    # Bonus Basis: 6000
    # Tax Savings: 6000 * 0.21 = 1260
    result = engine.evaluate_us_macrs_2026(10000, "2024-05-15")
    assert result.rule_id == "US_MACRS_2026"
    assert result.eligible is True
    assert result.amount == 1260
    assert result.trace["bonus_rate"] == 0.60
    assert result.trace["tax_bracket"] == 0.21

    # Test case 2: 2025 service date (40% bonus)
    # Cost: 10000
    # Bonus Basis: 4000
    # Tax Savings: 4000 * 0.21 = 840
    result = engine.evaluate_us_macrs_2026(10000, "2025-01-01")
    assert result.amount == 840
    assert result.trace["bonus_rate"] == 0.40

    # Test case 3: 2026 service date (20% bonus)
    # Cost: 10000
    # Bonus Basis: 2000
    # Tax Savings: 2000 * 0.21 = 420
    result = engine.evaluate_us_macrs_2026(10000, "2026-12-31")
    assert result.amount == 420
    assert result.trace["bonus_rate"] == 0.20

    # Test case 4: 2027 service date (0% bonus)
    result = engine.evaluate_us_macrs_2026(10000, "2027-01-01")
    assert result.amount == 0
    assert result.trace["bonus_rate"] == 0.0

    # Test case 5: Custom tax bracket
    # 2024 (60%), Cost 10000 -> Basis 6000
    # Tax: 6000 * 0.30 = 1800
    result = engine.evaluate_us_macrs_2026(10000, "2024-05-15", tax_bracket_percent=0.30)
    assert result.amount == 1800
    assert result.trace["tax_bracket"] == 0.30
