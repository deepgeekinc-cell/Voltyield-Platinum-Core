from pydantic import BaseModel
from typing import List

class TelemetryData(BaseModel):
    sensor: str
    value: float

class TelemetryBatch(BaseModel):
    batch_id: str
    region: str = "US"
    asset_cost: float = 0.0
    is_heavy_duty: bool = False
    qualified_zone: bool = False
    data: List[TelemetryData]
