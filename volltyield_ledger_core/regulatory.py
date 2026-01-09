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

    def get_fingerprint(self) -> str:
        return hashlib.sha256(self.version.encode()).hexdigest()
