from typing import Protocol, Any, Dict, List, Optional
from abc import ABC, abstractmethod
import hashlib
import json
from .models import TelemetryEvent

# --- Vault Interface ---
class Vault(ABC):
    @abstractmethod
    def store_tokens(self, client_id: str, access_token: str, refresh_token: str):
        pass

    @abstractmethod
    def get_tokens(self, client_id: str) -> Optional[Dict[str, str]]:
        pass

class InMemoryEncryptedVault(Vault):
    """
    Simulates an encrypted vault. In production, this would interface with
    AWS Secrets Manager, HashiCorp Vault, or similar.
    """
    def __init__(self):
        self._storage = {}

    def _encrypt(self, data: str) -> str:
        # Placeholder for encryption logic
        return f"encrypted:{data}"

    def _decrypt(self, data: str) -> str:
        # Placeholder for decryption logic
        if data.startswith("encrypted:"):
            return data.replace("encrypted:", "")
        return data

    def store_tokens(self, client_id: str, access_token: str, refresh_token: str):
        self._storage[client_id] = {
            "access_token": self._encrypt(access_token),
            "refresh_token": self._encrypt(refresh_token)
        }

    def get_tokens(self, client_id: str) -> Optional[Dict[str, str]]:
        data = self._storage.get(client_id)
        if not data:
            return None
        return {
            "access_token": self._decrypt(data["access_token"]),
            "refresh_token": self._decrypt(data["refresh_token"])
        }

# --- Receipt Parser Interface ---
class ReceiptData(Dict):
    merchant: str
    kwh: float
    cost_minor: int
    timestamp: str
    receipt_link: str

class ReceiptParser(ABC):
    @abstractmethod
    def parse(self, file_content: bytes, filename: str) -> ReceiptData:
        pass

class MockReceiptParser(ReceiptParser):
    def parse(self, file_content: bytes, filename: str) -> ReceiptData:
        # In a real scenario, this would call Taggun/Mindee API
        # Here we mock based on assumption it's a valid receipt for the demo
        return {
            "merchant": "VoltStation",
            "kwh": 50.0,
            "cost_minor": 2500, # $25.00
            "timestamp": "2025-06-15T10:00:00Z",
            "receipt_link": filename
        }

# --- Telemetry Service Interface ---
class TelemetryService(ABC):
    @abstractmethod
    def find_match(self, asset_id: str, timestamp: str) -> Optional[Dict[str, Any]]:
        pass

class MockTelemetryService(TelemetryService):
    def find_match(self, asset_id: str, timestamp: str) -> Optional[Dict[str, Any]]:
        # Mock finding an event near the timestamp
        # In production, query the database/ledger
        return {
            "asset_id": asset_id,
            "timestamp": "2025-06-15T10:02:00Z", # Within 5 mins variance
            "gps": "37.7749,-122.4194",
            "kwh": 50
        }

class TelemetryAdapter(Protocol):
    def fetch_events(self, start_time: str, end_time: str) -> List[TelemetryEvent]:
        ...

class SamsaraAdapter:
    def __init__(self, client: Any = None):
        self.client = client

    def fetch_events(self, start_time: str, end_time: str) -> List[TelemetryEvent]:
        # Mock implementation
        return []

class GeotabAdapter:
    def __init__(self, client: Any = None):
        self.client = client

    def fetch_events(self, start_time: str, end_time: str) -> List[TelemetryEvent]:
        # Mock implementation
        return []
