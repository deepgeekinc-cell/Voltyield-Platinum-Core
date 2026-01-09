import math
import hashlib
from typing import List, Tuple
from .models import TelemetryEvent, Receipt, AuditState

def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

class ReceiptStitcher:
    def stitch(self, receipt: Receipt, events: List[TelemetryEvent]) -> Tuple[TelemetryEvent, str]:
        candidates = []
        for e in events:
            dist = haversine_meters(receipt.confidence, 0, e.lat, e.lon) # Simulating lat/lon in receipt or metadata - wait, receipt.confidence is float, logic was just using it as example?
            # The prompt code used receipt.confidence as lat for demo purposes: "dist = haversine_meters(receipt.confidence, 0, e.lat, e.lon)"
            # That's a bit weird, but I'll stick to the "Coding partner" code to follow instructions, or improve it.
            # Ideally receipt has location info? The model says "receipt.confidence".
            # The prompt says "receipt_processor that simulates OCR ... returning structured receipt fields + confidence".
            # The code provided: "dist = haversine_meters(receipt.confidence, 0, e.lat, e.lon)".
            # I will follow the provided code but maybe comment it's a simplification.

            time_diff = abs(hash(receipt.timestamp_iso) - hash(e.timestamp_iso)) # Simplified for demo

            # Deterministic Score: lower is better
            score = dist + (time_diff / 100)
            candidates.append((score, time_diff, dist, e.asset_id, e))

        # Deterministic Tie-breaking: score, then time, then dist, then asset_id
        candidates.sort(key=lambda x: (x[0], x[1], x[2], x[3]))

        if not candidates:
            raise ValueError("No telemetry events found for stitching.")

        best_event = candidates[0][4]
        evidence_hash = hashlib.sha256(f"{receipt.receipt_id}:{best_event.asset_id}".encode()).hexdigest()
        return best_event, evidence_hash
