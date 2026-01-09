from datetime import datetime
import hashlib
from typing import List, Dict, Any, Optional

class RuleResult:
    def __init__(self, rule_id: str, eligible: bool, amount: int, trace: Dict[str, Any]):
        self.rule_id = rule_id
        self.eligible = eligible
        self.amount = amount
        self.trace = trace

class RegulatoryEngine:
    def __init__(self, rulepack_version: str):
        self.version = rulepack_version

    def evaluate_us_45w(self, asset_cost_minor: int, vehicle_weight_lbs: int, is_electric: bool = True) -> RuleResult:
        """
        US Section 45W Commercial Clean Vehicle Credit.
        Logic: 30% of basis for EVs (15% hybrids).
        Caps: $7,500 if < 14,000 lbs, $40,000 if >= 14,000 lbs.
        """
        rate = 0.30 if is_electric else 0.15
        credit_amount = int(asset_cost_minor * rate)

        cap = 4000000 if vehicle_weight_lbs >= 14000 else 750000

        final_amount = min(credit_amount, cap)

        trace = {
            "weight_lbs": vehicle_weight_lbs,
            "rate": rate,
            "uncapped_amount": credit_amount,
            "cap": cap
        }
        return RuleResult("US_45W", True, final_amount, trace)

    def evaluate_30c(self, tract_geoid: str, service_date: str, is_eligible_tract: bool) -> RuleResult:
        """US Section 30C Infrastructure Credit."""
        trace = {"geoid": tract_geoid, "date": service_date}
        eligible = (
            len(tract_geoid) == 11 and
            service_date <= "2026-06-30" and
            is_eligible_tract
        )
        return RuleResult("US_30C", eligible, 100000 if eligible else 0, trace)

    def evaluate_uk_mtd(self, digital_links_compliant: bool) -> RuleResult:
        """UK MTD Compliance Link."""
        return RuleResult("UK_MTD", digital_links_compliant, 0, {"compliant": digital_links_compliant})

    def evaluate_uk_vat_recovery(self, net_amount_minor: int, unbroken_lineage: bool) -> RuleResult:
        """UK VAT Recovery with MTD Digital Links check."""
        # VAT is typically 20% in UK.
        # Rule fails if lineage is broken.
        vat_amount = int(net_amount_minor * 0.20)
        eligible = unbroken_lineage
        trace = {
            "unbroken_lineage": unbroken_lineage,
            "basis_amount": net_amount_minor,
            "calculated_vat": vat_amount
        }
        return RuleResult("UK_VAT", eligible, vat_amount if eligible else 0, trace)

    def evaluate_us_macrs_2026(self, asset_cost_minor: int, placed_in_service_date: str, tax_bracket_percent: float = 0.21) -> RuleResult:
        """
        US MACRS Bonus Depreciation Rule (US_MACRS_2026).
        Calculates Depreciation Tax Shield based on bonus depreciation rates.
        """
        year = int(placed_in_service_date[:4])

        bonus_rate = 0.0
        if year == 2024:
            bonus_rate = 0.60
        elif year == 2025:
            bonus_rate = 0.40
        elif year == 2026:
            bonus_rate = 0.20

        # Avoid float math where possible using integer arithmetic for rate application
        bonus_basis = 0
        if year == 2024:
            bonus_basis = (asset_cost_minor * 60) // 100
        elif year == 2025:
            bonus_basis = (asset_cost_minor * 40) // 100
        elif year == 2026:
            bonus_basis = (asset_cost_minor * 20) // 100

        tax_savings = int(bonus_basis * tax_bracket_percent)

        trace = {
            "bonus_rate": bonus_rate,
            "tax_bracket": tax_bracket_percent
        }

        return RuleResult("US_MACRS_2026", True, tax_savings, trace)

    def get_fingerprint(self) -> str:
        return hashlib.sha256(self.version.encode()).hexdigest()
