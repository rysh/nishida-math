# src/lp/entailment.py
from __future__ import annotations

from collections.abc import Iterator, Sequence
from itertools import product

from gl.formula import Formula

from lp.evaluator import DESIGNATED, Lit, evaluate_lp

LP_VALUES: tuple[Lit, ...] = ("t", "b", "f")


def all_lp_valuations(atoms: Sequence[str]) -> Iterator[dict[str, Lit]]:
    """Yield all 3^|atoms| LP valuations over the supplied atom order."""
    for values in product(LP_VALUES, repeat=len(atoms)):
        yield dict(zip(atoms, values, strict=True))


def entails_lp(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool:
    """Brute-force LP entailment over all 3^|atoms| valuations.

    Γ ⊨_LP φ iff every valuation designating all formulas in Γ also designates φ.
    """
    for valuation in all_lp_valuations(atoms):
        if all(evaluate_lp(premise, valuation) in DESIGNATED for premise in premises):
            if evaluate_lp(conclusion, valuation) not in DESIGNATED:
                return False
    return True
