from .client import NHTSAClient
from .ui import ConsoleUI
from voltyield_ledger_core.battery import BatteryPassport, BatteryHealthEvent
from voltyield_ledger_core.regulatory import RegulatoryEngine

class ShowroomApp:
    def run(self):
        ui = ConsoleUI()
        api = NHTSAClient()
        guardian = BatteryPassport()
        reg = RegulatoryEngine("v2026.2")

        ui.banner()
        print("")
        
        # Default is a real Tesla Model S VIN
        vin = ui.get_input("VIN", "5YJSA1E21LF") 
        soh = float(ui.get_input("SOH %", "96"))
        cost = int(ui.get_input("Cost", "50000"))

        print("")
        ui.type_writer(f">> INGESTING: {vin}")
        ui.type_writer(">> CONNECTING TO NHTSA GOVERNMENT DATABASE...")
        
        data = api.decode_vin(vin)
        if data and data.get('make'):
            ui.type_writer(f">> IDENTITY VERIFIED: {data['year']} {data['make']} {data['model']}")
            if data.get('plant'):
                ui.type_writer(f">> MFG PLANT: {data['plant']}")
        else:
            ui.type_writer(">> MANUAL OVERRIDE: VIN LOOKUP FAILED")

        grade = guardian.calculate_resale_grade(BatteryHealthEvent(soh=soh, cycle_count=100, max_cell_temp_delta=1.0))
        
        # Mocking the strict payload for the demo
        geo = {"payload": {"tract_geoid": "00000000000", "is_30c_eligible_tract": True}, "hash": "mock"}
        reg.evaluate_us_30c_strict(geo, "2026-01-01")

        print("-" * 60)
        ui.print_kv("BATTERY GRADE:", grade['grade'])
        ui.print_kv("TAX SHIELD:", f"${cost * 0.60:,.2f}")
        print("-" * 60)
