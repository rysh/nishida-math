from __future__ import annotations

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from gl.countermodel_verifier import verify_countermodel
from gl.formula import And, Box, Formula, Iff, Imp, Not, Or, atom, bot, modal_depth
from gl.kripke_search import prove_gl as prove_kripke
from gl.tableau import prove_gl as prove_tableau

_ATOMS = [atom("p"), atom("q"), atom("r")]
_BASE = st.one_of(st.just(bot()), st.sampled_from(_ATOMS))


@st.composite
def formula_strategy(draw, max_modal_depth: int = 3, max_size: int = 7) -> Formula:
    if max_size <= 1:
        return draw(_BASE)
    choices = ["base", "not"]
    if max_size >= 3:
        choices.extend(["and", "or", "imp", "iff"])
    if max_modal_depth > 0:
        choices.append("box")
    kind = draw(st.sampled_from(choices))
    if kind == "base":
        return draw(_BASE)
    if kind == "not":
        return Not(draw(formula_strategy(max_modal_depth=max_modal_depth, max_size=max_size - 1)))
    if kind == "box":
        return Box(draw(formula_strategy(max_modal_depth=max_modal_depth - 1, max_size=max_size - 1)))

    left_size = draw(st.integers(min_value=1, max_value=max_size - 2))
    right_size = max_size - 1 - left_size
    left = draw(formula_strategy(max_modal_depth=max_modal_depth, max_size=left_size))
    right = draw(formula_strategy(max_modal_depth=max_modal_depth, max_size=right_size))
    if kind == "and":
        return And(left, right)
    if kind == "or":
        return Or(left, right)
    if kind == "imp":
        return Imp(left, right)
    if kind == "iff":
        return Iff(left, right)
    raise AssertionError(kind)


@settings(max_examples=1000, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(formula_strategy(max_modal_depth=3, max_size=7))
def test_tableau_and_kripke_search_agree(formula: Formula):
    assert modal_depth(formula) <= 3
    t = prove_tableau(formula)
    k = prove_kripke(formula)
    assert t.status == k.status, {"formula": formula.to_json(), "tableau": t.to_json(), "kripke": k.to_json()}
    assert not (t.status == "proved" and t.countermodel is not None)
    assert not (k.status == "proved" and k.countermodel is not None)
    if t.status == "refuted":
        assert t.countermodel is not None
        assert k.countermodel is not None
        assert verify_countermodel(formula, t.countermodel)
        assert verify_countermodel(formula, k.countermodel)
