# volltyield-ledger-core

Deterministic infrastructure for auditing EV infrastructure incentives.

## Setup
1. `pip install -e ".[dev]"`

## Running Tests
`pytest tests/test_deterministic.py`

## Running the Demo
`python -m volltyield_ledger_core.cli demo`

## Determinism Proof
The system uses:
1. **Canonical JSON**: Sorted keys and no whitespace.
2. **Chain Hashing**: Each ledger entry incorporates the hash of the previous state.
3. **Anti-Double-Count**: Unique keys derived from `RuleID + EvidenceHash`.
4. **Basis Guard**: Consumes basis slices deterministically to prevent over-claiming.

# VoltYield Platinum

**VoltYield Platinum** is a comprehensive asset management engine for EV battery storage. It combines regulatory tax logic, battery health grading, and actuarial risk assessment into a single pipeline.

## Features

### 1. Regulatory Engine (Tax)
Calculates US MACRS Bonus Depreciation based on the TCJA phase-out schedule:
* **2024:** 60% Bonus
* **2025:** 40% Bonus
* **2026:** 20% Bonus
* **2027+:** 0% Bonus (Standard MACRS only)

### 2. Battery Guardian (Asset Grading)
Evaluates battery telemetry to assign resale grades:
* **Platinum:** SOH > 94% AND Abuse Ratio < 30%.
* **Gold:** SOH > 85%.
* **Distressed:** SOH < 80% OR Any Thermal Events (> 45°C).

### 3. Syndicator (Privacy & Risk)
* **Anonymization:** Strips VIN, Driver Name, and GPS before export.
* **Risk Scoring:** Prioritizes "High Abuse" (Fast Charge > 80%) as a disqualifier for insurance premiums.

## Installation

```bash
pip install .
```
