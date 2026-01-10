from fastapi.testclient import TestClient
from voltyield_ledger_core.api import app

client = TestClient(app)

def test_casualty_shield_upload():
    # Mock uploading an insurance declaration
    files = {'files': ('insurance_declaration.pdf', b'fake content', 'application/pdf')}
    response = client.post("/ingest/files", files=files)
    assert response.status_code == 200
    data = response.json()

    assert "alert" in data
    assert data["alert"] == "TAX_EVENT_IMMINENT"
    forensics = data["casualty_forensics"]
    assert forensics["insurance_payout_taxable"] == 10000000
    assert forensics["section_1033_deadline"] == "2028-12-31" # 2026 + 2 years
    assert forensics["wv_property_tax_refund"] == "ELIGIBLE"
