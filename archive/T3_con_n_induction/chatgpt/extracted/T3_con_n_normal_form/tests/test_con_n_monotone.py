# tests/test_con_n_monotone.py
import pytest
import gl.formula as gf
from gl.tableau import prove_gl

bot = gf.bot
box = gf.box
neg = gf.neg


def imp(A, B):
    """A → B, with small compatibility fallbacks for formula-builder names."""
    for name in ("imp", "implies", "arrow"):
        if hasattr(gf, name):
            return getattr(gf, name)(A, B)
    for name in ("or_", "disj", "vee"):
        if hasattr(gf, name):
            return getattr(gf, name)(neg(A), B)
    raise AttributeError("gl.formula must provide imp/implies/arrow or or_/disj/vee")


def Con(n):
    """Con_n の定義通り（再帰）"""
    if n == 0:
        return neg(box(bot()))
    return neg(box(neg(Con(n - 1))))


@pytest.mark.parametrize("n", range(9))
def test_con_n_monotone(n):
    """GL ⊢ Con_{n+1} → Con_n"""
    formula = imp(Con(n + 1), Con(n))
    result = prove_gl(formula)
    assert result.status == "proved", \
        f"Con_{{{n+1}}} → Con_{n} が GL で証明できない: {result}"
