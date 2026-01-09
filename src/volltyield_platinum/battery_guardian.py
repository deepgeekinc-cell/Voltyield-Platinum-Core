from dataclasses import dataclass
from typing import Dict, Any, Union

@dataclass
class BatteryHealthEvent:
    soh_percent: float
    cycle_count: int
    fast_charge_count: int
    max_temp_c: float

class BatteryPassport:
    def calculate_resale_grade(self, event: BatteryHealthEvent) -> Dict[str, Union[str, float]]:
        # 1. Abuse Check
        is_abuse = False
        if event.cycle_count > 0:
            if event.fast_charge_count > (0.30 * event.cycle_count):
                is_abuse = True

        # 2. Thermal Check
        is_thermal_event = event.max_temp_c > 45.0

        # 3. Grading Logic

        # GRADE C (Distressed): SOH < 80% OR Thermal Event
        if event.soh_percent < 80.0 or is_thermal_event:
            return {"impact": "PENALTY", "value_adj": -0.25}

        # GRADE A (Platinum): SOH > 94% AND No Abuse
        if event.soh_percent > 94.0 and not is_abuse:
            return {"impact": "PREMIUM", "value_adj": 0.15}

        # GRADE B (Gold): SOH > 85%
        # Note: This executes if not Grade A (so SOH <= 94 OR Abuse present)
        # But must be > 85.
        if event.soh_percent > 85.0:
            return {"impact": "STANDARD", "value_adj": 0.0}

        # Fallback for gap [80.0, 85.0]
        return {"impact": "UNCERTIFIED", "value_adj": 0.0}
