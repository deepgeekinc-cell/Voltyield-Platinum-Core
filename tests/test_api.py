from fastapi.testclient import TestClient
from voltyield_ledger_core.api import app
import pytest

client = TestClient(app)

def test_certify_v001_dummy():
    # Test the hardcoded/mocked V-001 behavior directly
    response = client.get("/certify/V-001")
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert data["asset_id"] == "V-001"

    # Check Certification (Action A)
    # Mock data had SOH 98.5, Abuse False -> Platinum
    assert data["certification"]["grade"] == "PLATINUM"
    assert data["certification"]["badge"] == "BLUE_CHECK_VERIFIED"
    assert data["certification"]["health_score"] == 98.5

    # Check Financial Forensics (Action B)
    forensics = data["financial_forensics"]
    assert forensics["total_captured_value"] > 0

    # Check breakdown items
    breakdown = forensics["breakdown"]
    # We expect MACRS, 45W, 30C, and the mocked LCFS
    rules = [item["rule"] for item in breakdown]
    assert "US_MACRS_2026" in rules
    assert "US_45W" in rules
    assert "US_LCFS_2026" in rules

    # Verify values logic
    # Mock cost 3,500,000. Date 2024 (60% bonus).
    # Bonus Basis = 3,500,000 * 0.60 = 2,100,000
    # Tax Savings = 2,100,000 * 0.21 = 441,000
    # Let's find MACRS item
    macrs_item = next(item for item in breakdown if item["rule"] == "US_MACRS_2026")
    assert macrs_item["value"] == 441000

    # Verify 45W value
    # 30% of 3,500,000 = 1,050,000. Cap <14k lbs is 750,000.
    r45w_item = next(item for item in breakdown if item["rule"] == "US_45W")
    assert r45w_item["value"] == 750000

    # Verify LCFS mock value
    lcfs_item = next(item for item in breakdown if item["rule"] == "US_LCFS_2026")
    assert lcfs_item["value"] == 15000

def test_certify_not_found():
    response = client.get("/certify/NON_EXISTENT")
    assert response.status_code == 404

def test_ingest_flow():
    # Test the ingestion endpoint and subsequent certification
    # Create valid payload
    payload = {
        "receipt": {
            "receipt_id": "REC-TEST-1",
            "vendor": "TestVendor",
            "amount_minor": 1000,
            "currency": "USD",
            "timestamp_iso": "2024-01-01T12:00:00Z",
            "confidence": 34.05
        },
        "events": [
            {
                "asset_id": "V-002",
                "timestamp_iso": "2024-01-01T12:00:00Z",
                "lat": 34.05,
                "lon": -118.24,
                "kwh_delivered": 100,
                "status": "CHARGING",
                "unbroken_lineage": True,
                # Add data for grading if we implement that lookup
                # Currently API looks at best_event. But Pydantic model TelemetryEvent
                # in models.py (which we haven't seen fully but used in cli.py)
                # might not have 'soh', etc.
                # Let's see if we can pass extra fields if Pydantic allows extra?
                # Or rely on the fallback defaults in the API code (95.0 SOH).
            }
        ]
    }

    # Ingest
    res_ingest = client.post("/ingest", json=payload)
    assert res_ingest.status_code == 200
    assert res_ingest.json()["asset_id"] == "V-002"

    # Certify V-002
    res_cert = client.get("/certify/V-002")
    assert res_cert.status_code == 200
    data = res_cert.json()
    assert data["asset_id"] == "V-002"
    # Should use default fallback SOH 95.0 -> Platinum
    assert data["certification"]["grade"] == "PLATINUM"
    assert data["certification"]["health_score"] == 95.0
