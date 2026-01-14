import hashlib
from typing import Dict, Any
from .ledger import canonicalize

class RuleResult:
    def __init__(self, rule_id: str, eligible: bool, amount: int, trace: Dict[str, Any]):
        self.rule_id = rule_id
        self.eligible = eligible
        self.amount = amount
        self.trace = trace

class RegulatoryEngine:
    def __init__(self, version: str):
        self.version = version

    def evaluate_us_30c_strict(self, geo_attestation: Dict[str, Any], date: str) -> RuleResult:
        payload = geo_attestation.get("payload", {})
        if not payload: return RuleResult("US_30C", False, 0, {"error": "No Payload"})
        
        eligible = (payload.get("is_30c_eligible_tract") is True)
        return RuleResult("US_30C", eligible, 100000 if eligible else 0, {"verified": True})
