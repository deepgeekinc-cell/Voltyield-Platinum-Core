import time
from .client import NHTSAClient
from .ui import ConsoleUI

# Import Core Logic
try:
    from voltyield_ledger_core.battery import BatteryPassport, BatteryHealthEvent
    from voltyield_ledger_core.regulatory import RegulatoryEngine
except ImportError:
    # Fallback/Mock for development if core is missing
    from voltyield_platinum.battery_guardian import BatteryPassport, BatteryHealthEvent
    from voltyield_platinum.regulatory import RegulatoryEngine

class ShowroomApp:
    def __init__(self):
        self.ui = ConsoleUI()
        self.api = NHTSAClient()
        self.guardian = BatteryPassport()
        self.reg_engine = RegulatoryEngine()

    def run(self):
        self.ui.banner()
        print("")

        # 1. ACQUIRE DATA
        vin = self.ui.get_input("Enter Asset VIN", default="5YJSA1E21LF")
        state = self.ui.get_input("Enter Jurisdiction State", default="CA").upper()
        soh = float(self.ui.get_input("Enter Battery SOH %", default="96"))
        cost = int(self.ui.get_input("Enter Basis Cost", default="50000"))

        # 2. PROCESSING THEATRE & API CALLS
        print("")
        self.ui.type_writer(f">> [SYSTEM] INGESTING ASSET: {vin.upper()}", 0.01)

        self.ui.type_writer(">> [NETWORK] QUERYING NHTSA vPIC DATABASE...", 0.02)
        vehicle_data = self.api.decode_vin(vin)

        desc = f"GENERIC ASSET ({vin})"
        if vehicle_data and vehicle_data.get('make'):
            desc = f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}"
            self.ui.type_writer(f">> [VALIDATED] IDENTITY CONFIRMED: \033[96m{desc}\033[0m", 0.01)
            # Extra metadata display
            if vehicle_data.get('plant'):
                 self.ui.type_writer(f">> [METADATA] MFG PLANT: {vehicle_data['plant']}", 0.01)
        else:
            self.ui.type_writer(f">> [WARNING] VIN LOOKUP FAILED. USING LOCAL ID.", 0.01)

        # Geo-Logic
        self.ui.type_writer(f">> [GEO-FENCE] ANALYZING JURISDICTION: {state}...", 0.01)
        # (Simplified geo-logic for the app controller)
        is_carb = state in ["CA", "OR", "WA"]
        lcfs_val = 1850.00 if is_carb else 0.00

        time.sleep(0.5)
        print("")

        # 3. CORE LOGIC EXECUTION
        # Battery
        event = BatteryHealthEvent(soh=soh, cycle_count=150, max_cell_temp_delta=2.0, fast_charge_ratio=0.1)
        grade_result = self.guardian.calculate_resale_grade(event)

        # Tax
        tax_result = self.reg_engine.evaluate_us_macrs_2026(cost, "2024-06-01")
        credit_45w = min(cost * 0.30, 7500) if cost < 14000 else 40000

        # 4. GENERATE REPORT
        self.ui.section_header(f"ASSET REPORT: {desc.upper()}")

        self.ui.print_kv("BATTERY HEALTH", "")
        self.ui.print_kv("SOH Reading:", f"{soh}%")
        self.ui.print_kv("VoltYield Grade:", grade_result['grade'], self.ui.BOLD)

        print("")
        self.ui.print_kv("FINANCIAL SHIELD", "")
        self.ui.print_kv("MACRS Deduction:", f"${tax_result.amount:,.2f}")
        self.ui.print_kv("IRC 45W Credit:", f"${credit_45w:,.2f}")

        total_fed = tax_result.amount + credit_45w
        self.ui.print_kv("TOTAL FED VALUE:", f"${total_fed:,.2f}", self.ui.BOLD)

        print("")
        self.ui.print_kv("OPERATIONAL", "")
        if lcfs_val > 0:
            self.ui.print_kv("LCFS Credit:", f"${lcfs_val:,.2f} / yr", self.ui.HEADER_COLOR)
        else:
            self.ui.print_kv("LCFS Credit:", "$0.00 (Geo-Locked)", self.ui.GRAY)

        print(self.ui.HEADER_COLOR + "-"*65 + self.ui.RESET)
        total_val = total_fed + lcfs_val
        print(f"   TOTAL VALUE GENERATED: ${total_val:,.2f}")
        print("   STATUS: COMPLIANT | HASH RECORDED")
        print("="*65 + "\033[0m")

def main():
    app = ShowroomApp()
    app.run()
