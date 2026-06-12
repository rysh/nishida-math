import pytest
from hypothesis import given, settings
from gl.formula import Iff
from gl.fixed_point import fixed_point as fp_main
from gl.fixed_point_alt import fixed_point as fp_alt
from gl.tableau import prove_gl
from .test_fixed_point_random import modalized_formulas

@settings(max_examples=50, deadline=None)
def test_two_algorithms_equivalence():
    """主実装（再帰）と代替実装（反復ループ）の証明論的一致を外部検証"""
    @given(modalized_formulas(max_depth=2))
    def run(A):
        H1 = fp_main(A, "p")
        H2 = fp_alt(A, "p")
        assert prove_gl(Iff(H1, H2)).status == "proved"
    run()