from typing import Dict, Any, Union
from dataclasses import dataclass

@dataclass
class BatteryHealthEvent:
    soh: float
    cycle_count: int
    max_cell_temp_delta: float
    fast_charge_ratio: float

class BatteryPassport:
    """
    Mock implementation of the Battery Guardian logic.
    In a real system, this would analyze internal resistance, thermal history, etc.
    """

    def calculate_resale_grade(self, input_data: Union[str, BatteryHealthEvent]) -> Dict[str, Any]:
        """
        Calculates the resale grade and value adjustment for a battery asset.
        Accepts either an asset_id (legacy/mock) or a BatteryHealthEvent (live/demo).
        """
        # Legacy/Mock support for string input
        if isinstance(input_data, str):
            asset_id = input_data
            if asset_id == "V-001":
                return {
                    "grade": "PLATINUM",
                    "badge": "BLUE_CHECK_VERIFIED",
                    "health_score": 98.5,
                    "value_adj": 0.15
                }
            elif asset_id == "V-BAD":
                return {
                    "grade": "C",
                    "badge": "DISTRESSED",
                    "health_score": 72.0,
                    "value_adj": -0.25
                }
            else:
                return {
                    "grade": "GOLD",
                    "badge": "VERIFIED",
                    "health_score": 90.0,
                    "value_adj": 0.0
                }

        # New logic for BatteryHealthEvent
        event = input_data

        # Logic:
        # Grade A (Platinum/SOH>94%/No Abuse) adds +0.15
        # Grade B (Gold/SOH>85%) adds 0.0
        # Grade C (Distressed/SOH<80% or Thermal) applies -0.25

        # Thermal Abuse Threshold (Assumed based on "NORMAL" being 2.0)
        is_thermal_issue = event.max_cell_temp_delta > 5.0

        if event.soh > 94 and not is_thermal_issue:
            return {"grade": "PLATINUM", "value_adj": 0.15}
        elif event.soh > 85 and not is_thermal_issue:
            return {"grade": "GOLD", "value_adj": 0.0}
        elif event.soh < 80 or is_thermal_issue:
            return {"grade": "C", "value_adj": -0.25}
        else:
            # Fallback for 80-85% (Gold/Standard)
            return {"grade": "GOLD", "value_adj": 0.0}
