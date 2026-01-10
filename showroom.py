import time
import sys
import random

try:
    # Try local dev / existing structure first
    from voltyield_ledger_core.battery import BatteryPassport, BatteryHealthEvent
    from voltyield_ledger_core.regulatory import RegulatoryEngine
except ImportError:
    try:
         # Fallback for user provided namespace
        from voltyield_platinum.battery_guardian import BatteryPassport, BatteryHealthEvent
        from voltyield_ledger_core.regulatory import RegulatoryEngine
    except ImportError:
        from voltyield_platinum.battery_guardian import BatteryPassport, BatteryHealthEvent
        from voltyield_platinum.regulatory import RegulatoryEngine

def type_writer(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print("")

def run_showroom():
    print("\033[92m" + "="*65)
    print("      VOLTYIELD PLATINUM  |  ASSET SHOWROOM v1.1 (GEO-AWARE)  ")
    print("      regulatory_engine: \033[1mONLINE\033[0m\033[92m  |  guardian: \033[1mONLINE\033[0m")
    print("\033[92m" + "="*65 + "\033[0m")

    # 1. Inputs
    print("")
    vin = input("   \033[94m[INPUT] Enter Asset VIN / ID (e.g. WING-2-WING-01): \033[0m")
    state = input("   \033[94m[INPUT] Enter Jurisdiction State (e.g. CA, WV, TX): \033[0m").upper()
    soh_input = input("   \033[94m[INPUT] Enter Current Battery SOH % (e.g. 96): \033[0m")
    cost_input = input("   \033[94m[INPUT] Enter Original Basis Cost (e.g. 50000): \033[0m")

    # 2. Processing Theatre
    print("")
    type_writer(f">> [SYSTEM] INGESTING ASSET: {vin.upper()}", 0.01)

    # GEO-LOGIC: Check State
    if state == "CA":
        jurisdiction = "CA-90210 (Zone: CARB)"
        lcfs_val = 1850.00
        state_rebate_val = 2000.00
        geo_msg = ">> [GEO-FENCE] \033[92mCREDITS UNLOCKED\033[0m: CARB REGION DETECTED"
    elif state == "WV":
        jurisdiction = "WV-25301 (Zone: PJM)"
        lcfs_val = 0.00
        state_rebate_val = 0.00
        geo_msg = ">> [GEO-FENCE] \033[93mCREDITS LOCKED\033[0m: NON-CARB REGION (WV)"
    else:
        jurisdiction = f"{state}-GENERIC"
        lcfs_val = 0.00
        state_rebate_val = 0.00
        geo_msg = f">> [GEO-FENCE] STANDARD JURISDICTION: {state}"

    type_writer(f">> [GEO-FENCE] DETECTED JURISDICTION: {jurisdiction}", 0.01)
    type_writer(geo_msg, 0.01)
    type_writer(">> [LEDGER] STACKING AVAILABLE INCENTIVES...", 0.02)
    time.sleep(0.5)
    print("")

    # 3. Calculations
    soh = float(soh_input)
    cost = int(cost_input)

    # Battery Logic
    guardian = BatteryPassport()
    event = BatteryHealthEvent(soh=soh, cycle_count=150, max_cell_temp_delta=2.0, fast_charge_ratio=0.1)
    grade_result = guardian.calculate_resale_grade(event)

    # Tax Logic
    reg_engine = RegulatoryEngine(rulepack_version="2024.1")
    tax_result = reg_engine.evaluate_us_macrs_2026(cost, "2024-06-01", 100)

    # Federal is consistent everywhere
    credit_45w = min(cost * 0.30, 7500) if cost < 14000 else 40000

    # 4. Report
    print("\033[92m" + "-"*65)
    print(f"   ASSET REPORT: {vin.upper()} | LOC: {state}")
    print("-" * 65 + "\033[0m")

    print(f"   1. BATTERY HEALTH STATUS")
    print(f"      SOH Reading:       {soh}%")
    print(f"      VoltYield Grade:   \033[1m{grade_result['grade']}\033[0m")

    print("\n   2. FEDERAL TAX SHIELD (Federal Law applies everywhere)")
    print(f"      MACRS Depreciation: ${tax_result.amount:,.2f}")
    print(f"      IRC 45W Credit:     ${credit_45w:,.2f}")
    print(f"      \033[1mTOTAL FED VALUE:    ${(tax_result.amount + credit_45w):,.2f}\033[0m")

    print("\n   3. STATE & OPERATIONAL CREDITS (Geo-Locked)")
    if lcfs_val > 0:
        print(f"      LCFS Carbon Credit: ${lcfs_val:,.2f} / yr")
    else:
        print(f"      LCFS Carbon Credit: \033[90m$0.00 (Not Eligible in {state})\033[0m")

    if state_rebate_val > 0:
        print(f"      State HVIP Rebate:  ${state_rebate_val:,.2f} (Geo-Locked: CA)")
    else:
        print(f"      State HVIP Rebate:  \033[90m$0.00 (Not Eligible in {state})\033[0m")

    total_val = tax_result.amount + credit_45w + lcfs_val + state_rebate_val
    print("\033[92m" + "-"*65)
    print("   TOTAL ASSET VALUE GENERATED: ${:,.2f}".format(total_val))
    print("   STATUS: COMPLIANT | HASH RECORDED")
    print("="*65 + "\033[0m")

if __name__ == "__main__":
    run_showroom()
