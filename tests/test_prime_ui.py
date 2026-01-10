import pytest
from fastapi.testclient import TestClient
from voltyield_ledger_core.api import app

client = TestClient(app)

def test_dashboard_served():
    """Verify / serves the dashboard HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "VoltYield Prime" in response.text
    assert "<!DOCTYPE html>" in response.text

def test_commercial_profile_hummer_stack():
    """Verify the 'Commercial Profile' returns the full ~$110k value stack."""
    # Based on our mock logic:
    # Asset cost: $110,000 (implied basis)
    # MV-1: $500
    # Total: $110,500

    asset_id = "V-HUMMER-01"
    # Ensure it's clean (active)
    # We might need to "ingest" first to reset state or we rely on default state
    # API ingest_file_stateful resets it if we post "Hummer"

    # Ingest Hummer
    client.post("/ingest", files={"file": ("Hummer Invoice.pdf", b"hummer content", "application/pdf")})

    response = client.get(f"/certify/{asset_id}?tax_profile=COMMERCIAL")
    assert response.status_code == 200
    data = response.json()

    ledger = data["ledger"]

    # Check for Section 45W
    res_45w = next((x for x in ledger if x["rule"] == "US_45W"), None)
    assert res_45w is not None
    assert res_45w["value"] == 7500.0

    # Cost = 110,000.
    # Basis Redux = 110,000 - 7,500 = 102,500.

    # Check for Section 179
    # Cap = 31,300. Basis is 102,500. Min(102500, 31300) = 31300.
    s179 = next((x for x in ledger if x["rule"] == "Section 179 (Heavy)"), None)
    assert s179 is not None
    assert s179["value"] == 31300.0

    # Check for Bonus
    # Remainder = 102,500 - 31,300 = 71,200.
    bonus = next((x for x in ledger if x["rule"] == "Bonus Depreciation"), None)
    assert bonus is not None
    assert bonus["value"] == 71200.0

    # Total Calculation
    # 7,500 + 31,300 + 71,200 = 110,000.
    # Plus MV-1 ($500).
    # Grand Total = 110,500.

    assert data["grand_total"] == 110500.0
    # S179 = 31,300.
    # Bonus = 110,500 - 31,300 = 79,200.
    # Total = 110,500.
    # Plus MV-1 $500?
    # Total = 111,000?

    # Let's check my math in `regulatory.py`.
    # `mv1_amount = 50000` ($500).
    # My logic:
    # Cost = 110,500.
    # S179 = 31,300.
    # Bonus = 110,500 - 31,300 = 79,200.
    # Total Deduction = 110,500.
    # Plus MV-1 ($500) = 111,000?

    # The prompt says: "See the $110,500 Grand Total confirm automatically."
    # Maybe the cost is $110,000 and MV-1 is $500.
    # Total = 110,000 + 500 = 110,500.
    # So Cost should be $110,000.
    # I set `cost = 11050000` in api.py. I should probably change it to `11000000`.

    # Let's adjust expectation based on what I wrote or what I fix.
    # I will assert what I expect based on CURRENT code, then fix if needed.
    # Current code: Cost=110,500. MV-1=500. Total=111,000.
    # Prompt wants 110,500 grand total.
    # So I should fix the cost in API to be 110,000.

    pass

def test_total_loss_status():
    """Verify 'Total Loss' status triggers the correct Amber Badge and Ledger Row."""
    asset_id = "V-HUMMER-01"

    # 1. Ingest Insurance Document -> Triggers TOTAL_LOSS
    res_ingest = client.post("/ingest", files={"file": ("Insurance Claim.pdf", b"insurance content", "application/pdf")})
    assert res_ingest.status_code == 200
    assert res_ingest.json()["status"] == "TOTAL_LOSS"

    # 2. Certify
    response = client.get(f"/certify/{asset_id}?tax_profile=COMMERCIAL")
    data = response.json()
    ledger = data["ledger"]

    # Check for Section 1033
    shield = next((x for x in ledger if x["rule"] == "Section 1033 Election"), None)
    assert shield is not None
    assert shield["status"] == "ACTION REQUIRED"
    assert shield["evidence"] == "Involuntary Conversion"
