import pytest
from gl.formula import bot, Box, Not, Iff, box_power
from gl.tableau import prove_gl

def Con(n: int):
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))

@pytest.mark.parametrize("n", range(9))
def test_con_n_normal_form(n: int):
    lhs = Con(n)
    rhs = Not(box_power(bot(), n + 1))
    result = prove_gl(Iff(lhs, rhs))
    assert result.status == "proved"
