import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Optional
from pydantic import BaseModel
from enum import Enum

from .ledger import ForensicLedger
from .regulatory import RegulatoryEngine

app = FastAPI(title="VoltYield Ledger API", version="0.2.0")

# Mount Static Files
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_path, "index.html"))

# Engines
engine = RegulatoryEngine(rulepack_version="v2026.1.1")
# We use a global ledger for simplicity in this demo structure
ledger = ForensicLedger()

class TaxProfile(str, Enum):
    PERSONAL = "PERSONAL"
    COMMERCIAL = "COMMERCIAL"

# Global mock DB
asset_db = {
    "V-HUMMER-01": {"status": "ACTIVE", "cost": 11000000, "weight": 9063, "state": "WV"}
}

@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """
    Mock OCR Logic to determine asset identity or status from file content (filename/bytes).
    """
    content = await file.read()
    filename = file.filename.lower()

    if "hummer" in filename:
        asset_id = "V-HUMMER-01"
        # Reset to active if re-ingesting asset
        asset_db[asset_id]["status"] = "ACTIVE"
        asset_db[asset_id]["cost"] = 11000000 # $110,000
        return {"asset_id": asset_id, "type": "HEAVY_EV"}

    if "insurance" in filename:
        asset_id = "V-HUMMER-01"
        asset_db[asset_id]["status"] = "TOTAL_LOSS"
        return {"status": "TOTAL_LOSS", "payout": 100000}

    return {"status": "UNKNOWN", "message": "Document not recognized"}

@app.get("/certify/{asset_id}")
def certify_asset(asset_id: str, tax_profile: TaxProfile = TaxProfile.COMMERCIAL):
    """
    Returns a ledger list containing the breakdown and grand_total.
    """
    asset_data = asset_db.get(asset_id, {"status": "ACTIVE", "cost": 11000000, "weight": 9063, "state": "WV"})

    status = asset_data["status"]
    cost = asset_data["cost"]
    weight = asset_data["weight"]
    state = asset_data["state"]

    ledger_items = []
    grand_total = 0

    results = engine.evaluate_prime_stack(
        vehicle_cost=cost,
        gvwr=weight,
        state=state,
        status=status,
        tax_profile=tax_profile
    )

    # Convert RuleResults to Prime Ledger Format
    for r in results:
        status_label = "VERIFIED"

        # Total Loss logic specific override
        if r.rule_id == "Section 1033 Election":
             status_label = "ACTION REQUIRED"

        ledger_items.append({
            "rule": r.rule_id,
            "evidence": r.evidence_label,
            "value": r.value_amount / 100.0, # Convert minor units to float for JSON
            "status": status_label
        })

        if r.value_amount > 0:
            grand_total += (r.value_amount / 100.0)

    return {
        "asset_id": asset_id,
        "ledger": ledger_items,
        "grand_total": grand_total
    }
