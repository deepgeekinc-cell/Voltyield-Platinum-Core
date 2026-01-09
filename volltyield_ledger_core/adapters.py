from typing import Protocol, Any, Dict, List
from .models import TelemetryEvent

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
