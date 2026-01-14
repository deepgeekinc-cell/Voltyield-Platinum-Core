VOLTYIELD PLATINUM CORE | DISCOVERY PACKAGE
============================================
Version: 2.0.0-ENTERPRISE
Date: 2026-01-10

CONTENTS:
1. voltyield_ledger_core/api.py
   - High-throughput FastAPI ingestion rail.
   - Handles concurrent telemetry streams from large fleets (10k+ assets).
   - Enforces Fleet ID authorization.

2. voltyield_ledger_core/ledger.py
   - Immutable Forensic Ledger.
   - Uses SHA-256 chain hashing for data integrity.
   - Enforces idempotency to prevent duplicate tax claims.

3. voltyield_ledger_core/regulatory.py
   - "The Brain" of the compliance engine.
   - Contains strict logic for US Section 30C (Infrastructure) and 45W (Commercial).
   - Enforces cryptographic verification of Geo-Attestation payloads.

USAGE:
Run the server: uvicorn voltyield_ledger_core.api:app --reload
