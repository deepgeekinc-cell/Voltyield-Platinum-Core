from typing import Dict, Any
from pydantic import BaseModel

class BatteryHealthEvent(BaseModel):
    soh: float
    cycle_count: int
    max_cell_temp_delta: float
    fast_charge_ratio: float = 0.0

class BatteryPassport:
    def calculate_resale_grade(self, event: BatteryHealthEvent) -> Dict[str, Any]:
        if event.soh >= 95 and event.max_cell_temp_delta < 3.0:
            return {"grade": "PLATINUM", "value_adj": 0.15}
        elif event.soh >= 90:
            return {"grade": "GOLD", "value_adj": 0.10}
        else:
            return {"grade": "SILVER", "value_adj": 0.05}
