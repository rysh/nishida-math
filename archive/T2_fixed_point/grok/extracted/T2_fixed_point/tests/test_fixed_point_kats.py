"""
tests/test_fixed_point_kats.py
Known Answer Tests（KATs）
engine (fixed_point) は prover を呼ばず、
テスト側で独立に gl.tableau.prove_gl または gl.kripke_search.prove_gl を呼んで検証する。
"""
import pytest
from gl.formula import atom, bot, Not, Box, Imp, Iff
from gl.fixed_point import fixed_point, substitute
from gl.tableau import prove_gl  # ← ここだけが prover 呼び（engine からは import しない）


def assert_fixed_point(A, p: str, expected_H):
    H = fixed_point(A, p)

    # 1. H が期待値と GL-equivalent か
    equiv_to_expected = Iff(H, expected_H)
    res1 = prove_gl(equiv_to_expected)
    assert res1.status == "proved", f"H not GL-equivalent to expected: {H} vs {expected_H}"

    # 2. 本来の固定点方程式 H ↔ A[p := H] が GL で証明されるか（最重要）
    fp_equation = Iff(H, substitute(A, p, H))
    res2 = prove_gl(fp_equation)
    assert res2.status == "proved", f"GL ⊬ H ↔ A[p:=H]: H={H}"


def test_godel_fixed_point():
    """KAT 1: Gödel sentence ¬□p の固定点は ¬□⊥"""
    A = Not(Box(atom("p")))
    assert_fixed_point(A, "p", Not(Box(bot())))


def test_henkin_fixed_point():
    """KAT 2: Henkin 文 □p の固定点は ⊤ (¬⊥) — Löb により inert"""
    A = Box(atom("p"))
    assert_fixed_point(A, "p", Not(bot()))


def test_lob_fixed_point():
    """KAT 3: Löb sentence □p → q の固定点は □q → q"""
    A = Imp(Box(atom("p")), atom("q"))
    assert_fixed_point(A, "p", Imp(Box(atom("q")), atom("q")))


def test_box_not_p_fixed_point():
    """KAT 4: □¬p の固定点は □⊥"""
    A = Box(Not(atom("p")))
    assert_fixed_point(A, "p", Box(bot()))
