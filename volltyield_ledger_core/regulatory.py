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

    def evaluate_us_45w(self, vehicle_weight_lbs: int, cost_basis_minor: int, is_tax_exempt: bool = False, is_ev: bool = True) -> RuleResult:
        """US Section 45W Commercial Clean Vehicle Credit."""
        # 1. Determine cap based on weight
        if vehicle_weight_lbs < 14000:
            cap_amount = 750000 # $7,500
        else:
            cap_amount = 4000000 # $40,000

        # 2. Determine rate (30% for EV, 15% for Hybrid)
        rate = 0.30 if is_ev else 0.15

        # 3. Calculate tentative credit
        tentative_credit = int(cost_basis_minor * rate)

        # 4. Final amount is lesser of tentative or cap
        final_amount = min(tentative_credit, cap_amount)

        # Trace
        trace = {
            "vehicle_weight_lbs": vehicle_weight_lbs,
            "cost_basis_minor": cost_basis_minor,
            "is_ev": is_ev,
            "cap_applied": cap_amount,
            "tentative_credit": tentative_credit,
            "is_tax_exempt": is_tax_exempt
        }

        return RuleResult("US_45W", True, final_amount, trace)

    def evaluate_us_macrs(self, cost_basis_minor: int) -> RuleResult:
        """US MACRS Depreciation Tax Shield (Placeholder)."""
        # Placeholder: Assume 5-year property, Year 1 (20%), 21% Tax Rate
        depreciation_deduction = cost_basis_minor * 0.20
        tax_shield = int(depreciation_deduction * 0.21)

        trace = {
            "method": "MACRS 5-year",
            "year": 1,
            "basis": cost_basis_minor,
            "tax_rate": 0.21
        }
        return RuleResult("US_MACRS", True, tax_shield, trace)

    def get_fingerprint(self) -> str:
        return hashlib.sha256(self.version.encode()).hexdigest()
