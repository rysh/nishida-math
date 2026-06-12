# tests/test_con_n_normal_form.py
import pytest
from gl.formula import bot, Box, Not, Iff, box_power
from gl.tableau import prove_gl


def Con(n: int):
    """Con_n の定義通り（再帰）"""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))


@pytest.mark.parametrize("n", range(9))
def test_con_n_normal_form(n: int):
    """Con_n ≡ ¬□^{n+1}⊥"""
    lhs = Con(n)
    rhs = Not(box_power(bot(), n + 1))
    result = prove_gl(Iff(lhs, rhs))
    assert result.status == "proved", \
        f"Con_{n} ≡ ¬□^{{{n + 1}}}⊥ の同値が GL で証明できない: {result}"
