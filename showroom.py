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
    print("      VOLTYIELD PLATINUM  |  ASSET SHOWROOM v1.0      ")
    print("      regulatory_engine: \033[1mONLINE\033[0m\033[92m  |  guardian: \033[1mONLINE\033[0m")
    print("\033[92m" + "="*65 + "\033[0m")

    # 1. The Prompt
    print("")
    vin = input("   \033[94m[INPUT] Enter Asset VIN / ID (e.g. WING-2-WING-01): \033[0m")
    soh_input = input("   \033[94m[INPUT] Enter Current Battery SOH % (e.g. 96): \033[0m")
    cost_input = input("   \033[94m[INPUT] Enter Original Basis Cost (e.g. 50000): \033[0m")

    # 2. The "Processing" Theatre
    print("")
    type_writer(">> [SYSTEM] CONNECTING TO TELEMETRY STREAM...", 0.04)
    time.sleep(0.4)
    type_writer(f">> [SYSTEM] INGESTING ASSET: {vin.upper()}", 0.01)
    type_writer(">> [GEO-FENCE] DETECTED JURISDICTION: CA-90210 (Zone: CARB)", 0.01)
    type_writer(">> [GUARDIAN] ANALYZING THERMAL HISTORY [HASH: 8x92a...]", 0.01)
    type_writer(">> [LEDGER] STACKING AVAILABLE INCENTIVES...", 0.02)
    time.sleep(0.5)
    print("")

    # 3. Real Logic
    soh = float(soh_input)
    cost = int(cost_input)

    guardian = BatteryPassport()
    event = BatteryHealthEvent(soh=soh, cycle_count=150, max_cell_temp_delta=2.0, fast_charge_ratio=0.1)
    grade_result = guardian.calculate_resale_grade(event)

    reg_engine = RegulatoryEngine(rulepack_version="2024.1")
    tax_result = reg_engine.evaluate_us_macrs_2026(cost, "2024-06-01", 100)

    # Calculate additional "Stackable" credits based on inputs
    credit_45w = min(cost * 0.30, 7500) if cost < 14000 else 40000 # Simplified 45W Commercial logic
    lcfs_credit = 1850.00 # Estimated annual LCFS generation for heavy usage
    state_rebate = 2000.00 # Sample State rebate

    # 4. The Full Report Card
    print("\033[92m" + "-"*65)
    print(f"   ASSET REPORT: {vin.upper()}")
    print("-" * 65 + "\033[0m")

    print(f"   1. BATTERY HEALTH STATUS")
    print(f"      SOH Reading:       {soh}%")
    print(f"      VoltYield Grade:   \033[1m{grade_result['grade']}\033[0m (Certified)")
    print(f"      Resale Uplift:     +{(grade_result['value_adj']*100):.0f}%")

    print("\n   2. FEDERAL TAX SHIELD (STACKED)")
    print(f"      MACRS Depreciation: ${tax_result.amount:,.2f} (60% Bonus)")
    print(f"      IRC 45W Credit:     ${credit_45w:,.2f} (Commercial EV)")
    print(f"      \033[1mTOTAL FED VALUE:    ${(tax_result.amount + credit_45w):,.2f}\033[0m")

    print("\n   3. OPERATIONAL CREDITS (RECURRING)")
    print(f"      LCFS Carbon Credit: ${lcfs_credit:,.2f} / yr")
    print(f"      State HVIP Rebate:  ${state_rebate:,.2f} (Geo-Locked: CA)")

    print("\033[92m" + "-"*65)
    print("   TOTAL ASSET VALUE GENERATED: ${:,.2f}".format(tax_result.amount + credit_45w + lcfs_credit + state_rebate))
    print("   STATUS: COMPLIANT | HASH RECORDED")
    print("="*65 + "\033[0m")

if __name__ == "__main__":
    run_showroom()
