from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AuditState(str, Enum):
    PROPOSED = "PROPOSED"
    MATCHED = "MATCHED"
    VERIFIED = "VERIFIED"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"

class TelemetryEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    asset_id: str
    timestamp_iso: str  # ISO8601 UTC
    lat: float
    lon: float
    kwh_delivered: int  # Minor units (mWh)
    status: str
    unbroken_lineage: bool = False  # For HMRC Digital Links
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Receipt(BaseModel):
    model_config = ConfigDict(frozen=True)
    receipt_id: str
    vendor: str
    amount_minor: int
    currency: str
    timestamp_iso: str
    confidence: float

class BasisSlice(BaseModel):
    model_config = ConfigDict(frozen=True)
    asset_id: str
    amount_minor: int
    category: str  # e.g., "EQUIPMENT", "INSTALLATION"
