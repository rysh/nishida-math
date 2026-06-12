import pytest
from hypothesis import given, settings
from gl.formula import Iff
from gl.fixed_point import fixed_point as fp_main
from gl.fixed_point_alt import fixed_point as fp_alt
from gl.tableau import prove_gl
from .test_fixed_point_random import modalized_formulas

@settings(max_examples=50, deadline=None)
@given(modalized_formulas(max_depth=2))
def test_two_algorithms_equivalence(A):
    """
    主アルゴリズムと代替アルゴリズムが出力する H1 と H2 が、
    構文的には異なっても GL において証明論的に同値であることを検証する。
    """
    H1 = fp_main(A, "p")
    H2 = fp_alt(A, "p")
    
    equiv = Iff(H1, H2)
    assert prove_gl(equiv).status == "proved", f"Algorithms diverged for {A}:\nMain: {H1}\nAlt: {H2}"