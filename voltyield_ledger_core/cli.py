import sys
import json
from .models import TelemetryEvent, Receipt, AuditState
from .ledger import ForensicLedger
from .processor import ReceiptStitcher
from .regulatory import RegulatoryEngine
from .yield_guard import YieldOptimizer

def run_demo():
    ledger = ForensicLedger()
    stitcher = ReceiptStitcher()
    engine = RegulatoryEngine(rulepack_version="v2026.1.1")
    optimizer = YieldOptimizer()

    # 1. Ingestion
    telemetry = [
        TelemetryEvent(
            asset_id="V-001",
            timestamp_iso="2026-01-01T12:00:00Z",
            lat=34.05,
            lon=-118.24,
            kwh_delivered=50000,
            status="CHARGING",
            unbroken_lineage=True  # Simulate good lineage
        )
    ]
    receipt = Receipt(receipt_id="REC-99", vendor="ChargePoint", amount_minor=1500,
                      currency="USD", timestamp_iso="2026-01-01T12:05:00Z", confidence=34.05)

    # 2. Stitching
    event, evidence_hash = stitcher.stitch(receipt, telemetry)

    # 3. Rules
    # US Rule
    res_30c = engine.evaluate_30c("06037101110", "2026-01-05", True)
    # UK Rule (simulating a UK scenario as well, or just evaluating all rules)
    res_mtd = engine.evaluate_uk_mtd(True)
    # UK VAT Rule
    res_vat = engine.evaluate_uk_vat_recovery(receipt.amount_minor, event.unbroken_lineage)

    # Setup Basis
    # We pretend we have enough basis for 30C but limited for others?
    # 30C amount is 100000. VAT is 300.
    # Let's say we have ample GENERAL basis.
    total_basis = {"GENERAL": 200000}

    # 4. Optimization
    # We pass all results. The optimizer will select based on basis availability.
    # Note: 30C returns 100000. VAT returns ~300.
    plan = optimizer.optimize([res_30c, res_mtd, res_vat], total_basis)

    # 5. Ledger Commit
    for item in plan.chosen_incentives:
        payload = {
            "type": "ELIGIBLE_PENNY",
            "amount": item.amount,
            "rule_id": item.rule_id,
            "evidence_hash": evidence_hash,
            "rulepack_fingerprint": engine.get_fingerprint(),
            "state": AuditState.COMMITTED
        }
        # ADC Key ensures we don't claim the same rule for the same evidence twice
        # We also incorporate basis slice info into ADC key if we want strictness,
        # but the prompt example used `rule_id:evidence_hash`.
        # The prompt "Enhancement 3" text said: "In the ledger.py, we now include the basis_slice in the anti_double_count_key..."
        # "ADC Key: ASSET_001:EQUIPMENT:SLICE_2026"
        # Since I don't have explicit slices in the payload above, I will stick to the previous pattern
        # OR attempt to construct a slice key.
        # "rule_id:evidence_hash" is safe for rule-level double dipping.
        # To represent the slice, I might append the category?
        # Let's stick to the prompt's `cli.py` example but updated.

        adc_key = f"{item.rule_id}:{evidence_hash}"
        entry = ledger.commit(payload, idempotency_key=f"req_{item.rule_id}_{receipt.receipt_id}", adc_key=adc_key)

        print(f"--- Committed {item.rule_id} ---")
        print(f"Entry Hash: {entry.entry_hash}")
        print(f"Chain Hash: {entry.chain_hash}")
        print(f"ADC Key:    {adc_key}")

    # Output specific fields required by prompt
    print("\n--- Summary ---")
    print(f"Entry Hashes: {[e.entry_hash for e in ledger.entries]}")
    print(f"Chain Hash: {ledger.entries[-1].chain_hash if ledger.entries else 'None'}")
    print(f"Rulepack Fingerprint: {engine.get_fingerprint()}")
    print(f"Anti-Double-Count Keys: {ledger.anti_double_count_keys}")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            run_demo()
        elif sys.argv[1] == "serve":
            import uvicorn
            uvicorn.run("voltyield_ledger_core.api:app", host="0.0.0.0", port=8000)
        else:
            print("Usage: python -m voltyield_ledger_core.cli [demo|serve]")
    else:
        print("Usage: python -m voltyield_ledger_core.cli [demo|serve]")

if __name__ == "__main__":
    main()
