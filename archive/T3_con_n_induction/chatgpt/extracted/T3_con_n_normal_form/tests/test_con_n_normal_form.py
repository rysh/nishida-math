# tests/test_con_n_normal_form.py
import pytest
from gl.formula import bot, box, neg, iff
from gl.tableau import prove_gl


def Con(n):
    """Con_n の定義通り（再帰）"""
    if n == 0:
        return neg(box(bot()))
    return neg(box(neg(Con(n - 1))))


def box_n(F, k):
    """□^k F"""
    for _ in range(k):
        F = box(F)
    return F


@pytest.mark.parametrize("n", range(9))
def test_con_n_normal_form(n):
    """Con_n ≡ ¬□^{n+1}⊥"""
    lhs = Con(n)
    rhs = neg(box_n(bot(), n + 1))
    result = prove_gl(iff(lhs, rhs))
    assert result.status == "proved", \
        f"Con_{n} ≡ ¬□^{{{n+1}}}⊥ の同値が GL で証明できない: {result}"
