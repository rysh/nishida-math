# src/classical/evaluator.py
from __future__ import annotations

from typing import Mapping

from gl.formula import Formula


def _require_unary(formula: Formula) -> Formula:
    if formula.arg is None:
        raise ValueError(f"malformed unary formula: {formula!r}")
    return formula.arg


def _require_binary(formula: Formula) -> tuple[Formula, Formula]:
    if formula.left is None or formula.right is None:
        raise ValueError(f"malformed binary formula: {formula!r}")
    return formula.left, formula.right


def evaluate_classical(formula: Formula, valuation: Mapping[str, bool]) -> bool:
    """Evaluate a Formula in classical propositional logic.

    This is the two-valued restriction of the non-modal machinery.  Any
    occurrence of ``type == "box"`` is rejected.
    """
    match formula.type:
        case "box":
            raise ValueError("classical evaluator does not accept modal formulas containing box")
        case "bot":
            return False
        case "atom":
            if formula.name is None:
                raise ValueError(f"malformed atom formula: {formula!r}")
            value = valuation[formula.name]
            if not isinstance(value, bool):
                raise ValueError(f"classical valuation for atom {formula.name!r} is not bool: {value!r}")
            return value
        case "not":
            return not evaluate_classical(_require_unary(formula), valuation)
        case "and":
            return all(evaluate_classical(arg, valuation) for arg in formula.args)
        case "or":
            return any(evaluate_classical(arg, valuation) for arg in formula.args)
        case "imp":
            left, right = _require_binary(formula)
            return (not evaluate_classical(left, valuation)) or evaluate_classical(right, valuation)
        case "iff":
            left, right = _require_binary(formula)
            return evaluate_classical(left, valuation) == evaluate_classical(right, valuation)
        case _:
            raise ValueError(f"unknown Formula type: {formula.type!r}")
