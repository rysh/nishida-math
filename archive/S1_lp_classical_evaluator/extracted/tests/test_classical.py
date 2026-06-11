# tests/test_classical.py
from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from classical.entailment import all_classical_valuations, entails_classical
from classical.evaluator import evaluate_classical
from gl.formula import And, Box, Formula, Iff, Imp, Not, Or, atom, bot
from lp.evaluator import evaluate_lp

ATOM_NAMES = ("p", "q", "r")


def formula_strategy(names: tuple[str, ...] = ATOM_NAMES) -> st.SearchStrategy[Formula]:
    leaves = st.one_of(st.just(bot()), st.sampled_from([atom(name) for name in names]))

    def extend(children: st.SearchStrategy[Formula]) -> st.SearchStrategy[Formula]:
        pairs = st.tuples(children, children)
        return st.one_of(
            children.map(Not),
            pairs.map(lambda pair: And(pair[0], pair[1])),
            pairs.map(lambda pair: Or(pair[0], pair[1])),
            pairs.map(lambda pair: Imp(pair[0], pair[1])),
            pairs.map(lambda pair: Iff(pair[0], pair[1])),
        )

    return st.recursive(leaves, extend, max_leaves=8)


def bool_valuation_strategy(names: tuple[str, ...] = ATOM_NAMES) -> st.SearchStrategy[dict[str, bool]]:
    return st.fixed_dictionaries({name: st.booleans() for name in names})


def as_lit(value: bool) -> str:
    return "t" if value else "f"


def test_classical_liar_formula_is_false_on_all_two_valuations() -> None:
    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    rows = [evaluate_classical(liar, valuation) for valuation in all_classical_valuations(["lambda"])]
    assert rows == [False, False]


def test_classical_vacuous_explosion_from_unsatisfiable_liar() -> None:
    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    p = atom("p")
    assert entails_classical([liar], p, ["lambda", "p"])
    assert entails_classical([liar], Not(p), ["lambda", "p"])
    assert entails_classical([liar], bot(), ["lambda"])


def test_classical_rejects_box_even_when_nested() -> None:
    p = atom("p")
    with pytest.raises(ValueError):
        evaluate_classical(Box(p), {"p": True})
    with pytest.raises(ValueError):
        evaluate_classical(And(p, Box(p)), {"p": True})


@given(formula=formula_strategy(), valuation=bool_valuation_strategy())
@settings(max_examples=100)
def test_classical_matches_lp_on_two_valued_restriction(
    formula: Formula, valuation: dict[str, bool]
) -> None:
    lp_valuation = {name: as_lit(value) for name, value in valuation.items()}
    assert evaluate_lp(formula, lp_valuation) == as_lit(evaluate_classical(formula, valuation))
