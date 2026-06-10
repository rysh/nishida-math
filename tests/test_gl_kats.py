from __future__ import annotations

import pytest

from gl.countermodel_verifier import verify_countermodel
from gl.formula import Box, Imp, Not, atom, bot, box_power, con
from gl.kripke_search import prove_gl as prove_kripke
from gl.tableau import prove_gl as prove_tableau


def assert_proved(formula):
    t = prove_tableau(formula)
    k = prove_kripke(formula)
    assert t.status == "proved", t.to_json()
    assert k.status == "proved", k.to_json()


def assert_refuted(formula):
    t = prove_tableau(formula)
    k = prove_kripke(formula)
    assert t.status == "refuted", t.to_json()
    assert k.status == "refuted", k.to_json()
    assert t.countermodel is not None
    assert k.countermodel is not None
    assert verify_countermodel(formula, t.countermodel)
    assert verify_countermodel(formula, k.countermodel)
    return t, k


def test_lob_axiom():
    p = atom("p")
    assert_proved(Imp(Box(Imp(Box(p), p)), Box(p)))


def test_4_axiom_is_derivable_in_gl():
    p = atom("p")
    assert_proved(Imp(Box(p), Box(Box(p))))


def test_second_incompleteness_form():
    # ¬□⊥ → ¬□¬□⊥
    assert_proved(Imp(Not(Box(bot())), Not(Box(Not(Box(bot()))))))


@pytest.mark.parametrize("n", range(5))
def test_con_monotonicity(n: int):
    # Con_{n+1} → Con_n, where Con_n ≡ ¬□^(n+1)⊥.
    assert_proved(Imp(con(n + 1), con(n)))


@pytest.mark.parametrize("n", range(5))
def test_con_strictness(n: int):
    # GL ⊬ Con_n → Con_{n+1}; every refutation must carry a valid model.
    _, kripke = assert_refuted(Imp(con(n), con(n + 1)))
    if n == 0:
        assert kripke.countermodel is not None
        assert kripke.countermodel["worlds"] == [0, 1]
        assert kripke.countermodel["rel"] == [[0, 1]]


def test_con_definition_has_off_by_one_intentionally():
    assert con(0).to_json() == Not(Box(bot())).to_json()
    assert con(1).to_json() == Not(Box(Box(bot()))).to_json()
    assert con(4).to_json() == Not(box_power(bot(), 5)).to_json()
