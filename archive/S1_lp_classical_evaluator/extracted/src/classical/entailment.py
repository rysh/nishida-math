# src/classical/entailment.py
from __future__ import annotations

from collections.abc import Iterator, Sequence
from itertools import product

from gl.formula import Formula

from classical.evaluator import evaluate_classical


def all_classical_valuations(atoms: Sequence[str]) -> Iterator[dict[str, bool]]:
    """Yield all 2^|atoms| classical valuations over the supplied atom order."""
    for values in product((False, True), repeat=len(atoms)):
        yield dict(zip(atoms, values, strict=True))


def entails_classical(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool:
    """Brute-force classical entailment over all 2^|atoms| valuations."""
    for valuation in all_classical_valuations(atoms):
        if all(evaluate_classical(premise, valuation) for premise in premises):
            if not evaluate_classical(conclusion, valuation):
                return False
    return True
