from typing import List, Dict
from .regulatory import RuleResult
from .models import BasisSlice

class YieldPlan:
    def __init__(self, chosen_incentives: List[RuleResult], total_yield: int):
        self.chosen_incentives = chosen_incentives
        self.total_yield = total_yield

class YieldOptimizer:
    def optimize(self, results: List[RuleResult], total_basis: Dict[str, int]) -> YieldPlan:
        """
        results: Available incentives
        total_basis: Map of category -> available minor units (e.g., {"EQUIPMENT": 500000})
        """
        # 1. Filter and prioritize by highest yield (Greedy Deterministic)
        eligible = [r for r in results if r.eligible]
        eligible.sort(key=lambda x: (-x.amount, x.rule_id))

        chosen = []
        remaining_basis = total_basis.copy()
        total_yield = 0

        for rule in eligible:
            # Check if this rule requires a specific basis category
            # For this demo, we assume rules consume from "GENERAL" unless specified in trace
            category = rule.trace.get("basis_category", "GENERAL")

            # If the rule doesn't specify a basis consumption amount, we assume it consumes its own amount
            # or 0 if it's a tax credit that doesn't reduce basis?
            # The prompt implies "stackable only up to 100% of the cost".
            # So the claim amount consumes the basis.
            # But wait, a 30% credit on $100k cost is $30k credit.
            # Does it consume $30k of basis or $100k?
            # Usually "basis" means the cost.
            # If I claim a credit ON the cost, I usually use up that cost "slot" if it's mutually exclusive.
            # If they stack, maybe I don't use it up.
            # The prompt says: "if two incentives are mutually exclusive... or stackable... optimizer must ensure sum of claims does not exceed underlying value."
            # It also says: "basis slices / claim scopes represented explicitly... solver prevents overlapping claims unless explicitly allowed."
            # The code snippet provided in the "Coding partner" response uses:
            # `required_amount = rule.amount`
            # `if remaining_basis... >= required_amount`
            # This implies the credit amount reduces the available basis dollar-for-dollar?
            # That seems like a simplification (credit vs basis), but I will follow the provided snippet exactly.

            required_amount = rule.amount

            # Deterministic double-dip check
            if remaining_basis.get(category, 0) >= required_amount:
                # Deduct from available basis
                remaining_basis[category] -= required_amount
                total_yield += required_amount
                chosen.append(rule)
            else:
                # Rule is skipped or partially applied if basis is exhausted
                continue

        return YieldPlan(chosen, total_yield)
