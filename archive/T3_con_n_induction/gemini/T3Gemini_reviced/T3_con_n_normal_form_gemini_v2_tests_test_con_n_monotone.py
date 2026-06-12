import pytest
from gl.formula import Imp
from gl.tableau import prove_gl
from test_con_n_normal_form import Con

@pytest.mark.parametrize("n", range(9))
def test_con_n_monotone(n: int):
    formula = Imp(Con(n + 1), Con(n))
    result = prove_gl(formula)
    assert result.status == "proved"
