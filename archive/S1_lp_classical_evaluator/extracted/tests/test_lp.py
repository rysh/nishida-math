# tests/test_lp.py
from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from gl.formula import And, Box, Formula, Iff, Imp, Not, Or, atom, bot
from lp.entailment import all_lp_valuations, entails_lp
from lp.evaluator import DESIGNATED, Lit, evaluate_lp

LP_VALUES: tuple[Lit, ...] = ("t", "b", "f")
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


def lp_valuation_strategy(names: tuple[str, ...] = ATOM_NAMES) -> st.SearchStrategy[dict[str, Lit]]:
    return st.fixed_dictionaries({name: st.sampled_from(LP_VALUES) for name in names})


def test_lp_negation_table() -> None:
    p = atom("p")
    assert evaluate_lp(Not(p), {"p": "t"}) == "f"
    assert evaluate_lp(Not(p), {"p": "b"}) == "b"
    assert evaluate_lp(Not(p), {"p": "f"}) == "t"


def test_lp_liar_formula_is_satisfied_at_b_only() -> None:
    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    rows = {
        valuation["lambda"]: evaluate_lp(liar, valuation)
        for valuation in all_lp_valuations(["lambda"])
    }
    assert rows == {"t": "f", "b": "b", "f": "f"}
    assert rows["b"] in DESIGNATED


def test_lp_mp_failure_witness() -> None:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(a, witness) in DESIGNATED
    assert evaluate_lp(Imp(a, b), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([a, Imp(a, b)], b, ["A", "B"])


def test_lp_ds_failure_witness() -> None:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(Or(a, b), witness) in DESIGNATED
    assert evaluate_lp(Not(a), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([Or(a, b), Not(a)], b, ["A", "B"])


def test_lp_rejects_box_even_when_nested() -> None:
    p = atom("p")
    with pytest.raises(ValueError):
        evaluate_lp(Box(p), {"p": "t"})
    with pytest.raises(ValueError):
        evaluate_lp(Not(Box(p)), {"p": "t"})


@given(formula=formula_strategy(), valuation=lp_valuation_strategy())
@settings(max_examples=100)
def test_lp_double_negation_is_value_preserving(formula: Formula, valuation: dict[str, Lit]) -> None:
    assert evaluate_lp(Not(Not(formula)), valuation) == evaluate_lp(formula, valuation)


@given(
    premises=st.lists(formula_strategy(("p", "q")), max_size=2),
    conclusion=formula_strategy(("p", "q")),
)
@settings(max_examples=75)
def test_lp_lambda_contradiction_is_inert_for_lambda_free_formulas(
    premises: list[Formula], conclusion: Formula
) -> None:
    lam = atom("lambda")
    lambda_contradiction = And(lam, Not(lam))
    assert entails_lp(premises + [lambda_contradiction], conclusion, ["p", "q", "lambda"]) == entails_lp(
        premises, conclusion, ["p", "q"]
    )
