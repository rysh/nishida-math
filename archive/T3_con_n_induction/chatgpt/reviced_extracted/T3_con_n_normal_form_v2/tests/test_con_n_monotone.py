# tests/test_con_n_monotone.py
import pytest
from gl.formula import bot, Box, Not, Imp
from gl.tableau import prove_gl


def Con(n: int):
    """Con_n の定義通り（再帰）"""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))


@pytest.mark.parametrize("n", range(9))
def test_con_n_monotone(n: int):
    """GL ⊢ Con_{n+1} → Con_n"""
    formula = Imp(Con(n + 1), Con(n))
    result = prove_gl(formula)
    assert result.status == "proved", \
        f"Con_{{{n + 1}}} → Con_{n} が GL で証明できない: {result}"
