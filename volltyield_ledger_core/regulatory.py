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
    rules_registry = {
        "US_45W_2026": {
            "effective_from": "2023-01-01",
            "effective_to": "2032-12-31",
            "jurisdiction": "US"
        }
    }

    def __init__(self, rulepack_version: str):
        self.version = rulepack_version

    def evaluate_us_45w(self, ref_date: str, vehicle_weight_lbs: int, sale_price_minor: int, is_tax_exempt_entity: bool) -> RuleResult:
        """US Commercial Clean Vehicle Credit (Section 45W)."""
        rule_meta = self.rules_registry["US_45W_2026"]

        # Sunset Check
        if not (rule_meta["effective_from"] <= ref_date <= rule_meta["effective_to"]):
            return RuleResult("US_45W_2026", False, 0, {"reason": "sunset_check_failed"})

        # Cap Determination
        if vehicle_weight_lbs < 14000:
            cap_limit = 750000  # $7,500 in minor units
        else:
            cap_limit = 4000000 # $40,000 in minor units

        # Credit Calculation
        calculated_15_percent = (sale_price_minor * 15) // 100
        final_amount = min(calculated_15_percent, cap_limit)

        trace = {
            "vehicle_weight": vehicle_weight_lbs,
            "cap_limit": cap_limit
        }

        return RuleResult("US_45W_2026", True, final_amount, trace)

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

    def get_fingerprint(self) -> str:
        return hashlib.sha256(self.version.encode()).hexdigest()
