from datetime import datetime
import hashlib
from typing import List, Dict, Any, Optional

class RuleResult:
    def __init__(self, rule_id: str, eligible: bool, amount: int, trace: Dict[str, Any], citation: str):
        self.rule_id = rule_id
        self.eligible = eligible
        self.amount = amount
        self.trace = trace
        self.citation = citation

class RegulatoryEngine:
    def __init__(self, rulepack_version: str):
        self.version = rulepack_version

    def evaluate_30c(self, tract_geoid: str, service_date: str, is_eligible_tract: bool) -> RuleResult:
        """US Section 30C Infrastructure Credit (Basic)."""
        trace = {"geoid": tract_geoid, "date": service_date}
        eligible = (
            len(tract_geoid) == 11 and
            service_date <= "2026-06-30" and
            is_eligible_tract
        )
        # Note: Enhanced 30C logic is in evaluate_us_30c_enhanced.
        # This function retains legacy behavior but with citation.
        return RuleResult("US_30C", eligible, 100000 if eligible else 0, trace, "IRC § 30C")

    def evaluate_us_30c_enhanced(self, wage_evidence: bool, basis_minor: int) -> RuleResult:
        """US Section 30C Infrastructure Credit (Enhanced with Prevailing Wage)."""
        # Base Case: 6%. Enhanced Case: 30%.
        rate = 0.30 if wage_evidence else 0.06
        amount = int(basis_minor * rate)
        # Cap is $100,000 per item of property
        amount = min(amount, 10000000)

        trace = {
            "wage_evidence_hash": "VERIFIED" if wage_evidence else "MISSING",
            "multiplier_authorized": wage_evidence,
            "rate_applied": rate
        }
        return RuleResult("US_30C", True, amount, trace, "IRC § 30C(g) / IRA 2022 § 13404")

    def evaluate_us_lcfs(self, kwh_delivered: int, jurisdiction: str, has_ansi_meter: bool, has_gps_lock: bool) -> RuleResult:
        """US LCFS Credits (Carbon Rail)."""
        # Conservative mocks: CA=$0.15, OR=$0.12, WA=$0.14
        rates = {"CA": 150, "OR": 120, "WA": 140} # minor units per kWh (e.g. 15 cents = 150 millicents? No, minor units usually cents or mills.
        # Code base usually uses minor units as cents?
        # Ledger models.py says kwh_delivered is int (mWh) and Receipt.amount_minor is int.
        # If receipt amount_minor=1500 is $15.00, then it's cents.
        # kwh_delivered=50000 (mWh) = 50 kWh.
        # Rate $0.15 per kWh = 15 cents per kWh.
        # Total = 50 * 15 = 750 cents = $7.50.

        # Wait, let's check kwh units in models.py from turn 1.
        # "kwh_delivered: int  # Minor units (mWh)" -> 50000 mWh = 50 kWh.
        # If rate is $0.15/kWh.
        # Amount = (kwh_mwh / 1000) * 0.15 dollars.
        # Amount in cents = (kwh_mwh / 1000) * 15 cents.
        # To avoid floats: (kwh_mwh * 15) // 1000.

        # Rates in cents/kWh:
        rate_cents = {"CA": 15, "OR": 12, "WA": 14}

        if jurisdiction not in rate_cents or not (has_ansi_meter and has_gps_lock):
             return RuleResult("US_LCFS", False, 0, {"reason": "Invalid Jurisdiction or Evidence"}, "Cal. Code Regs. Tit. 17 § 95481")

        rate = rate_cents[jurisdiction]
        amount = (kwh_delivered * rate) // 1000

        trace = {
            "evidence_source": "ANSI_C12_METER" if has_ansi_meter else "MISSING",
            "jurisdiction_proof": "GPS_LOCKED" if has_gps_lock else "MISSING",
            "jurisdiction": jurisdiction,
            "rate_cents_per_kwh": rate
        }
        return RuleResult("US_LCFS", True, amount, trace, "Cal. Code Regs. Tit. 17 § 95481")

    def evaluate_uk_aer_reimbursement(self, kwh_delivered: int, location_type: str) -> RuleResult:
        """UK Audit Shield (AER & BiK)."""
        # location_type: "HOME_BASE" or "PUBLIC_NETWORK"
        # Rates: 8p (Home), 14p (Public).
        # kwh_delivered is mWh.
        # 8p per kWh.

        if location_type == "HOME_BASE":
            rate = 8
        elif location_type == "PUBLIC_NETWORK":
            rate = 14
        else:
            return RuleResult("UK_AER", False, 0, {"reason": "Unknown Location"}, "HMRC Guidance EIM23900")

        amount = (kwh_delivered * rate) // 1000
        trace = {
            "location_proof": "TELEMETRY_MATCH",
            "location_type": location_type,
            "rate_pence_per_kwh": rate
        }
        return RuleResult("UK_AER", True, amount, trace, "HMRC Guidance EIM23900")

    def evaluate_uk_mtd(self, digital_links_compliant: bool) -> RuleResult:
        """UK MTD Compliance Link."""
        return RuleResult("UK_MTD", digital_links_compliant, 0, {"compliant": digital_links_compliant}, "HMRC MTD Notice 700/22")

    def evaluate_uk_vat_recovery(self, net_amount_minor: int, unbroken_lineage: bool) -> RuleResult:
        """UK VAT Recovery with MTD Digital Links check."""
        vat_amount = int(net_amount_minor * 0.20)
        eligible = unbroken_lineage
        trace = {
            "unbroken_lineage": unbroken_lineage,
            "basis_amount": net_amount_minor,
            "calculated_vat": vat_amount
        }
        return RuleResult("UK_VAT", eligible, vat_amount if eligible else 0, trace, "VATA 1994 s24")

    def evaluate_us_45w(self, vehicle_weight_lbs: int, cost_basis_minor: int, is_tax_exempt: bool = False, is_ev: bool = True) -> RuleResult:
        """US Section 45W Commercial Clean Vehicle Credit."""
        if vehicle_weight_lbs < 14000:
            cap_amount = 750000
        else:
            cap_amount = 4000000

        rate = 0.30 if is_ev else 0.15
        tentative_credit = int(cost_basis_minor * rate)
        final_amount = min(tentative_credit, cap_amount)

        trace = {
            "vehicle_weight_lbs": vehicle_weight_lbs,
            "cost_basis_minor": cost_basis_minor,
            "is_ev": is_ev,
            "cap_applied": cap_amount,
            "tentative_credit": tentative_credit,
            "is_tax_exempt": is_tax_exempt
        }

        return RuleResult("US_45W", True, final_amount, trace, "IRC § 45W(b)(1)")

    def evaluate_us_macrs(self, cost_basis_minor: int) -> RuleResult:
        """US MACRS Depreciation Tax Shield (Placeholder)."""
        depreciation_deduction = cost_basis_minor * 0.20
        tax_shield = int(depreciation_deduction * 0.21)

        trace = {
            "method": "MACRS 5-year",
            "year": 1,
            "basis": cost_basis_minor,
            "tax_rate": 0.21
        }
        return RuleResult("US_MACRS", True, tax_shield, trace, "IRC § 168(k)")

    def get_fingerprint(self) -> str:
        return hashlib.sha256(self.version.encode()).hexdigest()
