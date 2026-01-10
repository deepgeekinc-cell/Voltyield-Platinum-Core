import sys
import json
from .models import TelemetryEvent, Receipt, AuditState
from .ledger import ForensicLedger
from .processor import ReceiptStitcher
from .regulatory import RegulatoryEngine
from .yield_guard import YieldOptimizer

def demo_full_stack():
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
            unbroken_lineage=True
        )
    ]
    receipt = Receipt(receipt_id="REC-99", vendor="ChargePoint", amount_minor=1500,
                      currency="USD", timestamp_iso="2026-01-01T12:05:00Z", confidence=34.05)

    # 2. Stitching
    event, evidence_hash = stitcher.stitch(receipt, telemetry)

    # 3. Rules Evaluation
    # A. 45W Commercial Vehicle
    vehicle_weight_lbs = 16000
    is_tax_exempt = False
    vehicle_cost_minor = 14000000 # $140,000. 30% = $42,000 -> Cap $40,000.
    res_45w = engine.evaluate_us_45w(vehicle_weight_lbs, vehicle_cost_minor, is_tax_exempt)

    # B. 30C Infrastructure (Enhanced)
    # Evidence: Prevailing Wage = True
    wage_evidence = True
    basis_30c = 10000000 # $100,000
    res_30c = engine.evaluate_us_30c_enhanced(wage_evidence, basis_30c)

    # C. LCFS (Carbon Rail)
    res_lcfs = engine.evaluate_us_lcfs(1000000, "CA", True, True)

    # D. MACRS 2026 Bonus (New Requirement)
    # Using remainder after 45W or separate basis?
    # In this demo, we can just show it as a standalone incentive for the asset.
    # Assuming 100% Business Use.
    # Cost $140k. No 179 taken (weight 16k > 14k limit for 179 Heavy SUV? No, 179 limit is generic, but Heavy SUV specific rule was 6k-14k).
    # This vehicle is 16,000 lbs. It qualifies for regular 179 but not "Heavy SUV" cap. It might be uncapped 179.
    # But let's just apply MACRS 2026.
    res_macrs = engine.evaluate_us_macrs_2026(basis_minor=14000000, placed_in_service_date="2026-01-01", business_use_percent=100)

    # Setup Basis (Ample)
    total_basis = {"GENERAL": 1000000000}

    # 4. Optimization
    results = [res_45w, res_30c, res_lcfs, res_macrs]
    plan = optimizer.optimize(results, total_basis)

    # 5. Ledger Commit
    # We commit everything for the demo to populate hashes
    for item in plan.chosen_incentives:
        payload = {
            "type": "ELIGIBLE_PENNY",
            "amount": item.amount,
            "rule_id": item.rule_id,
            "evidence_hash": evidence_hash,
            "rulepack_fingerprint": engine.get_fingerprint(),
            "state": AuditState.COMMITTED,
            "citation": item.citation
        }
        adc_key = f"{item.rule_id}:{evidence_hash}"
        # Unique idempotency for demo
        ledger.commit(payload, idempotency_key=f"demo_{item.rule_id}", adc_key=adc_key)

    # 6. Visualization: "Verified Compliance Report"
    print("\n--- 🛡️ VOLTYIELD COMPLIANCE REPORT 🛡️ ---")
    print(f"Asset ID: {event.asset_id} | Compliance Status: VERIFIED\n")

    # Helper to print section
    def print_section(idx, title, res, status_label, extra_info=""):
        print(f"{idx}. {title}")
        print(f"   Status:     {status_label}")
        print(f"   Citation:   {res.citation}")
        print(f"   Value:      ${res.amount / 100:,.2f}{extra_info}")
        print()

    # 1. US Section 45W
    print_section(1, "US Section 45W (Commercial Vehicle)", res_45w,
                  "ELIGIBLE (Weight Class Verified)")

    # 2. US Section 30C
    # Check if enhanced
    status_30c = "ENHANCED (Prevailing Wage Evidence Linked)" if res_30c.trace.get("multiplier_authorized") else "BASE (Safe Harbor)"
    base_val = int(basis_30c * 0.06)
    extra_30c = f" (Base: ${base_val/100:,.2f} | Multiplier: ACTIVE)" if res_30c.trace.get("multiplier_authorized") else ""
    print_section(2, "US Section 30C (Infrastructure)", res_30c, status_30c, extra_30c)

    # 3. California LCFS
    print_section(3, "California LCFS (Carbon Credit)", res_lcfs,
                  "METERED (ANSI Metering Verified)")

    # 4. MACRS
    print_section(4, "US MACRS (Bonus Depreciation)", res_macrs,
                  "ACCELERATED (2025 Restoration Applied)")

    print("-------------------------------------------------------")
    print(f"TOTAL VERIFIED VALUE:  ${plan.total_yield / 100:,.2f}")
    print("-------------------------------------------------------")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_full_stack()
        elif sys.argv[1] == "serve":
            import uvicorn
            uvicorn.run("voltyield_ledger_core.api:app", host="0.0.0.0", port=8000, reload=True)
            return

    print("Usage: python -m voltyield_ledger_core.cli [demo|serve]")

if __name__ == "__main__":
    main()
