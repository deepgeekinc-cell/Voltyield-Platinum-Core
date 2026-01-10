import pytest
from fastapi.testclient import TestClient
from voltyield_ledger_core.api import app, ledger, get_global_vault, get_receipt_parser, get_telemetry_service
import hashlib
from voltyield_ledger_core.ledger import canonicalize
from voltyield_ledger_core.adapters import MockReceiptParser, MockTelemetryService

client = TestClient(app)

def test_connect_telematics():
    response = client.post("/connect/telematics", json={"provider": "ONSTAR", "api_key": "secret"})
    assert response.status_code == 200
    assert response.json() == {"status": "CONNECTED"}

def test_oauth_flow():
    # 1. Authorize
    auth_resp = client.get("/connect/authorize?client_id=123&redirect_uri=http://localhost/cb")
    assert auth_resp.status_code == 200
    assert "authorization_url" in auth_resp.json()
    assert "client_id=123" in auth_resp.json()["authorization_url"]

    # 2. Callback
    callback_resp = client.post("/connect/callback", json={
        "client_id": "123",
        "client_secret": "secret",
        "code": "auth_code_xyz",
        "redirect_uri": "http://localhost/cb"
    })
    assert callback_resp.status_code == 200
    data = callback_resp.json()
    assert "access_token" in data
    assert data["access_token"] == "mock_access_token_auth_code_xyz"

    # 3. Verify Vault
    vault = get_global_vault()
    tokens = vault.get_tokens("123")
    assert tokens is not None
    assert tokens["access_token"] == "mock_access_token_auth_code_xyz"

def test_webhook_charging():
    event_data = {
        "event_type": "CHARGING_START",
        "timestamp": "2025-06-15T12:00:00Z",
        "data": {"kwh": 10, "station_id": "S1"}
    }

    # Send Webhook
    response = client.post("/webhooks/charging", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NOTARIZED"
    assert "hash" in data

    # Calculate expected hash
    expected_hash = hashlib.sha256(canonicalize(event_data)).hexdigest()
    assert data["hash"] == ledger.entries[-1].entry_hash # Note: This might be fragile if other tests run in parallel or sequence, but for now single thread is fine.

    # Send Duplicate
    response_dup = client.post("/webhooks/charging", json=event_data)
    assert response_dup.status_code == 200
    assert response_dup.json()["status"] == "DUPLICATE"

def test_receipt_ingest_and_verification():
    # Mock receipt file
    receipt_content = b"Mock PDF Content"
    files = {"file": ("receipt.pdf", receipt_content, "application/pdf")}

    # We can override dependency here if we wanted to test different scenarios,
    # but for now we rely on the default mocks in api.py which are enough for this test.

    response = client.post("/ingest/receipt",
        files=files,
        data={"asset_id": "hummer-01"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "VERIFIED"
    assert "certificate_hash" in data

    # Check details
    details = data["details"]
    assert details["asset_id"] == "hummer-01"
    assert details["receipt_data"]["receipt_link"] == "receipt.pdf"

    # Verify Hash logic: AssetID + Timestamp + GPS + kWh + ReceiptLink
    telemetry = details["telemetry_match"]
    receipt = details["receipt_data"]
    combined = f"{details['asset_id']}{telemetry['timestamp']}{telemetry['gps']}{telemetry['kwh']}{receipt['receipt_link']}"
    expected_hash = hashlib.sha256(combined.encode()).hexdigest()

    assert data["certificate_hash"] == expected_hash

def test_consumer_view_zero_percent():
    # Hummer EV, 0% Business Use -> $1,000 Charger Credit
    response = client.get("/certify/hummer-01?business_use_percent=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total_value"] == 100000
    assert data["certificate_type"] == "CONSUMER_HOME_CHARGING"

def test_pro_view_hundred_percent():
    # Hummer EV, 100% Business Use
    # Cost: 110,000. Weight: 9000. Date: June 2025.
    # Sec 179: 31,300 (Cap)
    # Remaining: 78,700
    # Bonus: 100% of 78,700 = 78,700
    # Total Deduction: 110,000.

    response = client.get("/certify/hummer-01?business_use_percent=100")
    assert response.status_code == 200
    data = response.json()

    results = {r["rule"]: r for r in data["results"]}

    # Verify Sec 179
    assert "US_SEC_179_HEAVY" in results
    r179 = results["US_SEC_179_HEAVY"]
    assert r179["amount"] == 3130000 # $31,300

    # Verify MACRS
    assert "US_MACRS_2026" in results
    rmacrs = results["US_MACRS_2026"]
    # 110000 - 31300 = 78700
    assert rmacrs["amount"] == 7870000

    # Verify Total
    assert data["total_deduction_first_year"] == 11000000

def test_pro_view_sixty_percent():
    # Hummer EV, 60% Business Use
    # Business Cost: 60% of 110,000 = 66,000.
    # Sec 179 Cap: 31,300. Deduction = 31,300 (since 66k > 31.3k).
    # Remaining Basis: 66,000 - 31,300 = 34,700.
    # Bonus: 100% of 34,700 = 34,700.
    # Total Deduction: 31,300 + 34,700 = 66,000.

    response = client.get("/certify/hummer-01?business_use_percent=60")
    assert response.status_code == 200
    data = response.json()

    assert data["total_deduction_first_year"] == 6600000
