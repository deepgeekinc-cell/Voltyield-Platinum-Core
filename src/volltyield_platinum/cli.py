import argparse
import sys
import json
from volltyield_platinum.battery_guardian import BatteryPassport, BatteryHealthEvent
from volltyield_platinum import syndicator

def run_demo(mode: str):
    print(f"Running Platinum Demo in {mode} mode...")

    if mode == "full_stack":
        # 1. Generate Sample Data
        print("\n--- 1. Ingesting Telemetry ---")
        raw_event = {
            "vin": "5YJ3E1EA1JF00001",
            "driver_name": "Jane Doe",
            "exact_gps": "34.0522,-118.2437",
            "make": "Tesla",
            "model": "Model 3",
            "battery_chemistry": "NCA",
            "zip_code": "90012",
            "soh_percent": 96.5,
            "cycle_count": 150,
            "fast_charge_count": 20, # 13% < 30%
            "max_temp_c": 35.0,
            "charge_patterns": {"home": 0.8, "supercharger": 0.2},
            "kwh_drawn": 45.0,
            "hour_of_day": 18
        }
        print(f"Raw Telemetry: {json.dumps(raw_event, indent=2)}")

        # 2. Battery Guardian Grading
        print("\n--- 2. Battery Guardian Certification ---")
        health_event = BatteryHealthEvent(
            soh_percent=raw_event["soh_percent"],
            cycle_count=raw_event["cycle_count"],
            fast_charge_count=raw_event["fast_charge_count"],
            max_temp_c=raw_event["max_temp_c"]
        )
        passport = BatteryPassport()
        grade = passport.calculate_resale_grade(health_event)
        print(f"Resale Grade: {json.dumps(grade, indent=2)}")

        # 3. Data Syndication (Anonymization)
        print("\n--- 3. Privacy Anonymization (GDPR/CCPA) ---")
        # Augment raw_event with calculated health metrics for syndication context if needed,
        # but syndicator functions take the dict.
        # Ensure keys match what syndicator expects (it expects 'soh', raw has 'soh_percent')
        # The syndicator test used 'soh', but my battery event uses 'soh_percent'.
        # Let's align the data for the syndicator.
        syndication_input = raw_event.copy()
        syndication_input["soh"] = raw_event["soh_percent"]
        syndication_input["thermal_events"] = 1 if raw_event["max_temp_c"] > 45.0 else 0
        syndication_input["fast_charge_ratio"] = raw_event["fast_charge_count"] / raw_event["cycle_count"] if raw_event["cycle_count"] > 0 else 0

        anonymized = syndicator.anonymize_for_export(syndication_input)
        print(f"Anonymized Payload: {json.dumps(anonymized, indent=2)}")

        # 4. Insurance Risk Scoring
        print("\n--- 4. Actuarial Risk Assessment ---")
        risk_score = syndicator.calculate_actuarial_risk(anonymized)
        print(f"Risk Profile: {json.dumps(risk_score, indent=2)}")

        # 5. Grid Utilization
        print("\n--- 5. Grid Stress Map ---")
        # Create a small batch to show aggregation
        batch_data = [
            anonymized,
            {
                "zip_code": "90012",
                "hour_of_day": 18,
                "kwh_drawn": 30.0
            },
            {
                "zip_code": "90210",
                "hour_of_day": 19,
                "kwh_drawn": 55.0
            }
        ]
        grid_map = syndicator.aggregate_grid_utilization(batch_data)
        print(f"Grid Aggregation (Zip:Hour -> kWh): {json.dumps(grid_map, indent=2)}")

def main():
    parser = argparse.ArgumentParser(description="Voltyield Platinum CLI")
    parser.add_argument("command", choices=["demo"], help="Command to run")
    parser.add_argument("--mode", required=True, help="Demo mode")

    args = parser.parse_args()

    if args.command == "demo":
        run_demo(args.mode)

if __name__ == "__main__":
    main()
