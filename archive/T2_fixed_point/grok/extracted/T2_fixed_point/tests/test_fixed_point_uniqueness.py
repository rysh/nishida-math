"""
tests/test_fixed_point_uniqueness.py
2つのアルゴリズム（main / alt）で得られた H1, H2 が
GL ⊢ H1 ↔ H2 であることを独立 prover で検証
"""
import pytest
from hypothesis import given, settings
from gl.formula import Iff
from gl.fixed_point import fixed_point as fp_main
from gl.fixed_point_alt import fixed_point as fp_alt
from gl.tableau import prove_gl
from gl.modalized import is_modalized_in

# 簡易 strategy（実プロジェクトでは本格的な modalized formula strategy に置換）
from tests.test_fixed_point_random import simple_modalized_formula_strategy


@settings(max_examples=100, deadline=None)
@given(A=simple_modalized_formula_strategy())
def test_main_alt_uniqueness(A):
    p = "p"
    if not is_modalized_in(A, p):
        return  # skip non-modalized
    H1 = fp_main(A, p)
    H2 = fp_alt(A, p)
    equiv = Iff(H1, H2)
    result = prove_gl(equiv)
    assert result.status == "proved", f"H1 and H2 not GL-equivalent: {H1} vs {H2}"
