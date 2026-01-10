import json
import hashlib
from typing import Dict, Any, Optional, List
from .models import AuditState

def canonicalize(data: Dict[str, Any]) -> bytes:
    """Deterministic JSON serialization: sorted keys, no whitespace, UTC strings."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

class LedgerEntry:
    def __init__(self, payload: Dict[str, Any], prev_hash: Optional[str] = None):
        self.payload = payload
        self.entry_hash = hashlib.sha256(canonicalize(payload)).hexdigest()
        self.prev_hash = prev_hash

        chain_input = (prev_hash or "") + self.entry_hash
        self.chain_hash = hashlib.sha256(chain_input.encode()).hexdigest()

class ForensicLedger:
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.idempotency_keys: set[str] = set()
        self.anti_double_count_keys: set[str] = set()

    def commit(self, payload: Dict[str, Any], idempotency_key: str, adc_key: Optional[str] = None) -> LedgerEntry:
        if idempotency_key in self.idempotency_keys:
            raise ValueError(f"Idempotency violation: {idempotency_key}")
        if adc_key and adc_key in self.anti_double_count_keys:
            raise ValueError(f"Double-count protection triggered: {adc_key}")

        prev_hash = self.entries[-1].chain_hash if self.entries else None
        entry = LedgerEntry(payload, prev_hash)

        self.entries.append(entry)
        self.idempotency_keys.add(idempotency_key)
        if adc_key:
            self.anti_double_count_keys.add(adc_key)
        return entry
