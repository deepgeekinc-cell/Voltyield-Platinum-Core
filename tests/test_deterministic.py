import pytest
from voltyield_ledger_core.ledger import ForensicLedger, canonicalize
from voltyield_ledger_core.yield_guard import YieldOptimizer
from voltyield_ledger_core.regulatory import RuleResult

def test_ledger_determinism():
    payload = {"amount": 100, "asset": "V1", "nested": {"z": 1, "a": 2}}

    l1 = ForensicLedger()
    e1 = l1.commit(payload, "idemp-1")

    l2 = ForensicLedger()
    e2 = l2.commit(payload, "idemp-1")

    assert e1.entry_hash == e2.entry_hash
    assert e1.chain_hash == e2.chain_hash
    assert canonicalize(payload) == b'{"amount":100,"asset":"V1","nested":{"a":2,"z":1}}'

def test_anti_double_count():
    l = ForensicLedger()
    l.commit({"val": 1}, "req1", adc_key="same_scope")
    with pytest.raises(ValueError, match="Double-count protection"):
        l.commit({"val": 1}, "req2", adc_key="same_scope")

def test_basis_exhaustion():
    # Define a basis of 1000
    total_basis = {"GENERAL": 1000}

    # Define two rules worth 600 each
    r1 = RuleResult("R1", True, 600, {})
    r2 = RuleResult("R2", True, 600, {})

    optimizer = YieldOptimizer()

    # Case 1: [r1, r2]
    plan1 = optimizer.optimize([r1, r2], total_basis.copy())
    assert len(plan1.chosen_incentives) == 1
    assert plan1.total_yield == 600
    assert plan1.chosen_incentives[0].rule_id == "R1" # Sorts by amount then ID, so R1 comes before R2? R2 > R1 string? R1.
    # Logic: sort key (-amount, rule_id). -600 same. "R1" < "R2".

    # Case 2: [r2, r1]
    plan2 = optimizer.optimize([r2, r1], total_basis.copy())
    assert len(plan2.chosen_incentives) == 1
    assert plan2.total_yield == 600
    # Deterministic sort ensures R1 is always chosen first if amounts are equal
    assert plan2.chosen_incentives[0].rule_id == "R1"

def test_end_to_end_determinism():
    # Run the logic twice and check chain hashes match
    from voltyield_ledger_core.cli import run_demo
    import sys
    from io import StringIO

    # Capture stdout to avoid clutter
    old_stdout = sys.stdout
    sys.stdout = mystdout1 = StringIO()

    run_demo()
    output1 = mystdout1.getvalue()

    sys.stdout = mystdout2 = StringIO()
    run_demo()
    output2 = mystdout2.getvalue()

    sys.stdout = old_stdout

    assert output1 == output2
