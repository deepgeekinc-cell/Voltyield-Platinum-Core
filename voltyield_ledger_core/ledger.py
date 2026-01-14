import json
import os
import hashlib
from datetime import datetime

# Absolute Path for the Ledger
LEDGER_PATH = "/home/deepgeekinc/Voltyield-Platinum-Core/audit_trail.log"

def get_last_hash():
    if not os.path.exists(LEDGER_PATH) or os.stat(LEDGER_PATH).st_size == 0:
        return "GENESIS_BLOCK"
    with open(LEDGER_PATH, "rb") as f:
        try:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode()
            return json.loads(last_line).get("hash", "ERROR")
        except:
            return "GENESIS_BLOCK"

def record_entry(batch_data: dict):
    prev_hash = get_last_hash()
    region = batch_data.get("region", "US")
    asset_cost = batch_data.get("asset_cost", 0)
    
    stack = {}
    
    # --- TRANS-ATLANTIC STACKING LOGIC ---
    if region == "US":
        # Sec 45W: Commercial Vehicle ($40k heavy / $7.5k light)
        stack["sec_45W_vehicle"] = 40000.00 if batch_data.get("is_heavy_duty") else 7500.00
        # Sec 30C: Infrastructure ($100k in qualified zones)
        stack["sec_30C_infra"] = 100000.00 if batch_data.get("qualified_zone") else 0.0
        # Sec 48: ITC Stack (30% Base + 10% Domestic + 10% Energy Community = 50% Total)
        stack["sec_48_itc_stack"] = asset_cost * 0.50
        # Voluntary Carbon Integrity Premium
        stack["carbon_yield"] = len(batch_data.get('data', [])) * 75.0
        
    elif region == "UK_EU":
        # UK Super Deduction (130% Capital Allowance)
        stack["uk_super_deduction"] = asset_cost * 1.30
        # EU Carbon Allowances (ETS Pricing)
        stack["eu_carbon_credits"] = len(batch_data.get('data', [])) * 85.0

    total_yield = sum(v for v in stack.values() if isinstance(v, (int, float)))

    entry_payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "jurisdiction": region,
        "stack_analysis": {k: f"${v:,.2f}" for k, v in stack.items()},
        "total_maximized_yield": f"${total_yield:,.2f}",
        "prev_hash": prev_hash,
        "status": "INKED_TO_RAIL"
    }
    
    # Cryptographic Chaining
    entry_json = json.dumps(entry_payload, sort_keys=True)
    entry_payload["hash"] = hashlib.sha256(entry_json.encode()).hexdigest()
    
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(entry_payload) + "\n")
        f.flush()
        os.fsync(f.fileno())
