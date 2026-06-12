# tests/test_con_n_monotone.py
import pytest
from gl.formula import bot, box, neg, implies
from gl.tableau import prove_gl
from test_con_n_normal_form import Con

@pytest.mark.parametrize("n", range(9))
def test_con_n_monotone(n):
    """Con_{n+1} → Con_n"""
    # Con_{n+1} -> Con_n が証明可能かテスト
    formula = implies(Con(n + 1), Con(n))
    result = prove_gl(formula)
    assert result.status == "proved", \
        f"Con_{n+1} → Con_n が GL で証明できない: {result}"