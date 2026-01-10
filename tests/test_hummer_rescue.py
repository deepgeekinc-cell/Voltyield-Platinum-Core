import pytest
from voltyield_ledger_core.api import app
from voltyield_ledger_core.regulatory import RegulatoryEngine
from fastapi.testclient import TestClient

client = TestClient(app)

def test_hummer_rescue_scenario():
    """
    Scenario: Hummer EV, 100% Business Use, Bought 2025, Totaled 2026.

    Assert:
    Entry Value: Section 179 ($31.3k) + Bonus ($78.7k) = Full Write-off.
    Exit Safety: Section 1033 Deadline = Dec 31, 2028.
    Refund: WV Property Tax Refund = Eligible.
    """

    # 1. Ingest Hummer Invoice (Mock OCR)
    # We simulate the file upload by passing a dummy file with the correct name.
    files = {
        "files": ("hummer_invoice.pdf", b"fake content", "application/pdf")
    }
    resp_ingest = client.post("/ingest", files=files)
    assert resp_ingest.status_code == 200
    data_ingest = resp_ingest.json()
    assert data_ingest["status"] == "EVIDENCE_STITCHED"
    assert data_ingest["asset_id"] == "V-HUMMER-01"

    # 2. Ingest Insurance Payout (Mock OCR)
    files_payout = {
        "files": ("insurance_payout.pdf", b"fake content", "application/pdf")
    }
    resp_payout = client.post("/ingest", files=files_payout)
    assert resp_payout.status_code == 200
    data_payout = resp_payout.json()
    assert data_payout["condition"] == "TOTALED"
    assert data_payout["asset_id"] == "V-HUMMER-01"

    # 3. Certify Asset
    resp_certify = client.get("/certify/V-HUMMER-01?business_use_percent=100")
    assert resp_certify.status_code == 200
    cert = resp_certify.json()

    # Verify Financial Forensics
    forensics = cert["financial_forensics"]
    breakdown = forensics["breakdown"]

    # Helper to find rule result
    def get_rule_result(rule_id):
        for item in breakdown:
            if item["rule_id"] == rule_id:
                return item
        return None

    # Check Section 179
    r_179 = get_rule_result("US_SEC_179_HEAVY")
    assert r_179 is not None
    assert r_179["status"] == "VERIFIED"
    # Cap is $31,300 -> 3130000 minor units
    assert r_179["amount"] == 3130000

    # Check Bonus Depreciation
    # Total Cost $110,000 -> 11000000 minor units
    # Remainder = 11000000 - 3130000 = 7870000 ($78,700)
    r_bonus = get_rule_result("US_BONUS_DEPR")
    assert r_bonus is not None
    assert r_bonus["amount"] == 7870000

    # Verify Full Write-off logic: 179 + Bonus = Cost
    total_deduction = r_179["amount"] + r_bonus["amount"]
    assert total_deduction == 11000000

    # Check Casualty Event (Exit Safety)
    r_casualty = get_rule_result("CASUALTY_EVENT")
    assert r_casualty is not None
    # We can't see the trace directly in the breakdown response unless we exposed it.
    # The API output structure in api.py:
    # "financial_breakdown.append({... "citation": ...})"
    # It doesn't include the trace.
    # However, the user requirement says: "Exit Safety: Section 1033 Deadline = Dec 31, 2028."
    # If the test needs to assert this, we should inspect the RegulatoryEngine directly or verify if the API exposes this info.
    # The API in `certify` returns `financial_breakdown` which has `rule_id`, `amount`, `citation`, `status`.
    # It does NOT return the trace.
    # To verify the trace values (deadline, refund), we might need to rely on the "Casualty Shield Alert" text or modify the API to return more info.
    # The prompt says "Return the 'Casualty Shield' alert."

    # Check Alert
    assert "alerts" in cert
    assert "Casualty Shield Active: Section 1033 & WV Refund Eligible" in cert["alerts"][0]

    # If we really want to verify the deadline and refund flag, we might need to unit test the engine directly as well.
    # Let's do that for robustness.

    engine = RegulatoryEngine("test")
    res_casualty = engine.evaluate_casualty_event(10000000, "2026-01-15")
    assert res_casualty.trace["section_1033_deadline"] == "2028-12-31"
    assert res_casualty.trace["mv1_refund"] is True
