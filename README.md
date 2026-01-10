# voltyield-ledger-core

Deterministic infrastructure for auditing EV infrastructure incentives.

## Setup
1. `pip install -e ".[dev]"`

## Running Tests
`pytest tests/test_deterministic.py`

## Running the Demo
`python -m voltyield_ledger_core.cli demo`

## Determinism Proof
The system uses:
1. **Canonical JSON**: Sorted keys and no whitespace.
2. **Chain Hashing**: Each ledger entry incorporates the hash of the previous state.
3. **Anti-Double-Count**: Unique keys derived from `RuleID + EvidenceHash`.
4. **Basis Guard**: Consumes basis slices deterministically to prevent over-claiming.
