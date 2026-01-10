import pytest
from fastapi.testclient import TestClient
from voltyield_ledger_core.api import app

client = TestClient(app)

def test_connect_telematics():
    response = client.post("/connect/telematics", json={"provider": "ONSTAR", "api_key": "secret"})
    assert response.status_code == 200
    assert response.json() == {"status": "CONNECTED"}

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
