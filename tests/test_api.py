from fastapi.testclient import TestClient
from voltyield_ledger_core.api import app
import json

client = TestClient(app)

def test_certify_asset():
    response = client.get("/certify/V-001")
    assert response.status_code == 200
    data = response.json()

    # 1. Verify Battery Health (Blue Check)
    assert data["asset_id"] == "V-001"
    assert data["certification"]["grade"] == "PLATINUM"
    assert data["certification"]["health_score"] == 98.5

    # 2. Verify Financial Forensics (Tax Shield)
    financials = data["financial_forensics"]
    assert financials["total_captured_value"] > 0
    # 45W ($40k) + 30C ($30k) + LCFS ($150) + MACRS ($5,880 from $140k basis * 0.2 * 0.21)
    # Total = 7015000 + 588000 = 7603000

    breakdown = financials["breakdown"]
    rule_ids = [item["rule_id"] for item in breakdown]
    assert "US_45W" in rule_ids
    assert "US_30C" in rule_ids
    assert "US_LCFS" in rule_ids
    assert "US_MACRS" in rule_ids

def test_ingest_flow():
    payload = {
        "telemetry": [
            {
                "asset_id": "V-001",
                "timestamp_iso": "2026-01-01T12:00:00Z",
                "lat": 34.05,
                "lon": -118.24,
                "kwh_delivered": 50000,
                "status": "CHARGING",
                "unbroken_lineage": True
            }
        ],
        "receipts": [
            {
                "receipt_id": "REC-API-1",
                "vendor": "ChargePoint",
                "amount_minor": 1500,
                "currency": "USD",
                "timestamp_iso": "2026-01-01T12:05:00Z",
                "confidence": 34.05
            }
        ]
    }

    # Updated to send data as 'data' form field since endpoint now expects that or JSON body handled specially
    # But since we support json_payload via Body logic (or just sending JSON if no files), let's try strict JSON.
    # The API code `json_payload: Optional[IngestRequest] = Body(None)` should capture it.

    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["committed_entries"]) == 1

    # Verify ingest persisted telemetry for later certify LCFS calc
