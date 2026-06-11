# src/lp/evaluator.py
from __future__ import annotations

from typing import Literal, Mapping, TypeAlias

from gl.formula import Formula

Lit: TypeAlias = Literal["t", "b", "f"]

DESIGNATED: frozenset[Lit] = frozenset({"t", "b"})
_LIT_ORDER: dict[Lit, int] = {"f": 0, "b": 1, "t": 2}
_ORDER_LIT: dict[int, Lit] = {0: "f", 1: "b", 2: "t"}


def _require_unary(formula: Formula) -> Formula:
    if formula.arg is None:
        raise ValueError(f"malformed unary formula: {formula!r}")
    return formula.arg


def _require_binary(formula: Formula) -> tuple[Formula, Formula]:
    if formula.left is None or formula.right is None:
        raise ValueError(f"malformed binary formula: {formula!r}")
    return formula.left, formula.right


def neg_lit(value: Lit) -> Lit:
    """Priest LP negation: ¬t=f, ¬b=b, ¬f=t."""
    if value == "t":
        return "f"
    if value == "b":
        return "b"
    if value == "f":
        return "t"
    raise ValueError(f"unknown LP literal: {value!r}")


def and_lit(left: Lit, right: Lit) -> Lit:
    """LP conjunction as min under f < b < t."""
    return _ORDER_LIT[min(_LIT_ORDER[left], _LIT_ORDER[right])]


def or_lit(left: Lit, right: Lit) -> Lit:
    """LP disjunction as max under f < b < t."""
    return _ORDER_LIT[max(_LIT_ORDER[left], _LIT_ORDER[right])]


def imp_lit(left: Lit, right: Lit) -> Lit:
    """LP material implication A → B := ¬A ∨ B."""
    return or_lit(neg_lit(left), right)


def iff_lit(left: Lit, right: Lit) -> Lit:
    """LP biconditional A ↔ B := (A → B) ∧ (B → A)."""
    return and_lit(imp_lit(left, right), imp_lit(right, left))


def evaluate_lp(formula: Formula, valuation: Mapping[str, Lit]) -> Lit:
    """Evaluate a Formula in Priest's Logic of Paradox.

    Formula values are ``"t"``, ``"b"``, and ``"f"``.  Any occurrence of
    ``type == "box"`` is rejected because the LP evaluator is intentionally
    non-modal.
    """
    match formula.type:
        case "box":
            raise ValueError("LP evaluator does not accept modal formulas containing box")
        case "bot":
            return "f"
        case "atom":
            if formula.name is None:
                raise ValueError(f"malformed atom formula: {formula!r}")
            value = valuation[formula.name]
            if value not in DESIGNATED and value != "f":
                raise ValueError(f"unknown LP literal for atom {formula.name!r}: {value!r}")
            return value
        case "not":
            return neg_lit(evaluate_lp(_require_unary(formula), valuation))
        case "and":
            value: Lit = "t"
            for arg in formula.args:
                value = and_lit(value, evaluate_lp(arg, valuation))
            return value
        case "or":
            value: Lit = "f"
            for arg in formula.args:
                value = or_lit(value, evaluate_lp(arg, valuation))
            return value
        case "imp":
            left, right = _require_binary(formula)
            return imp_lit(evaluate_lp(left, valuation), evaluate_lp(right, valuation))
        case "iff":
            left, right = _require_binary(formula)
            return iff_lit(evaluate_lp(left, valuation), evaluate_lp(right, valuation))
        case _:
            raise ValueError(f"unknown Formula type: {formula.type!r}")
