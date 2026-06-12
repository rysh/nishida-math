# tests/test_con_n_consistency.py
"""Cross-component consistency tests for the Con_n index.

The simulation spec §2.3 fixes a single normal form: Con_n ≡ ¬□^{n+1}⊥.
Four different components encode this index independently:

  - src/gl/formula.py            con(n) helper
  - src/gl/fixed_point.py        Gödel fixed point of ¬□p
  - src/gl/letterless.py         letterless_normal_form(con(n))
  - tests/test_con_n_normal_form Con(n) recursive helper

S2 once surfaced a near-collision (Löb instance collapse made
Not(Box(Not(Box(bot)))) reduce to Con_0, not Con_1). The pins at the
bottom of this file guard against a regression where any of those
indices drifts by one.

Every equivalence claim here is checked by the independent
gl.tableau.prove_gl prover; reducers and fixed-point engines are never
allowed to grade themselves.
"""
from __future__ import annotations

import pytest

from gl.formula import Box, Iff, Not, atom, bot, box_power, con
from gl.fixed_point import fixed_point
from gl.letterless import letterless_normal_form
from gl.tableau import prove_gl


def RecursiveCon(n: int):
    """Mirror of the T3 recursive Con(n) helper.

    Kept inline because the tests directory is not importable as a package
    (only ``src`` is on ``pythonpath``).  Any drift between this definition
    and ``tests/test_con_n_normal_form.py::Con`` is itself a regression and
    is caught by ``test_formula_con_matches_recursive_helper``.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(RecursiveCon(n - 1))))


def _assert_gl_equiv(lhs, rhs, label: str) -> None:
    result = prove_gl(Iff(lhs, rhs))
    assert result.status == "proved", f"{label}: GL ⊬ {lhs!r} ↔ {rhs!r} ({result.status})"


@pytest.mark.parametrize("n", range(4))
def test_formula_con_is_syntactically_normal_form(n: int) -> None:
    """con(n) must be ``Not(box_power(bot(), n + 1))`` exactly (no GL detour)."""
    assert con(n).to_json() == Not(box_power(bot(), n + 1)).to_json()


@pytest.mark.parametrize("n", range(4))
def test_formula_con_matches_recursive_helper(n: int) -> None:
    """The T3 recursive Con(n) is GL-equivalent to the formula-module con(n)."""
    _assert_gl_equiv(con(n), RecursiveCon(n), f"con({n}) vs RecursiveCon({n})")


def test_godel_fixed_point_equals_con_zero() -> None:
    """The T2 fixed point of ¬□p must be GL-equivalent to Con_0 = ¬□⊥ (§2.2 KAT 1)."""
    H = fixed_point(Not(Box(atom("p"))), "p")
    _assert_gl_equiv(H, con(0), "fixed_point(¬□p, p) vs con(0)")


@pytest.mark.parametrize("n", range(4))
def test_letterless_reducer_preserves_con_index(n: int) -> None:
    """letterless_normal_form(con(n)) must be GL-equivalent to ¬□^{n+1}⊥."""
    nf = letterless_normal_form(con(n))
    _assert_gl_equiv(nf, Not(box_power(bot(), n + 1)), f"NF(con({n}))")


def test_lob_collapse_pin_not_box_not_box_bot_is_con_zero() -> None:
    """Pin for the S2 finding.

    Not(Box(Not(Box(bot())))) collapses to Con_0 (≡ ¬□⊥), not Con_1, because
    the inner Not(Box(bot())) is propositionally equivalent to
    Imp(Box(bot()), bot()), and the Löb instance □(□⊥→⊥) → □⊥ together with
    the trivial converse reduces the outer Box to □⊥.
    """
    expr = Not(Box(Not(Box(bot()))))
    nf = letterless_normal_form(expr)
    _assert_gl_equiv(nf, Not(box_power(bot(), 1)), "NF(¬□¬□⊥) vs Con_0")
    _assert_gl_equiv(nf, con(0), "NF(¬□¬□⊥) vs con(0)")


def test_pin_not_box_box_bot_is_con_one() -> None:
    """Neighbour pin: the syntactically similar Not(Box(Box(bot()))) really is Con_1.

    Together with the previous test this peg pair documents that the S2
    correction was about Löb collapse, not about the Con_n index itself.
    """
    expr = Not(Box(Box(bot())))
    nf = letterless_normal_form(expr)
    _assert_gl_equiv(nf, Not(box_power(bot(), 2)), "NF(¬□□⊥) vs Con_1")
    _assert_gl_equiv(nf, con(1), "NF(¬□□⊥) vs con(1)")
