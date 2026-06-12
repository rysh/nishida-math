import pytest
from hypothesis import given, settings, strategies as st
from gl.formula import atom, bot, Not, And, Or, Imp, Iff, Box
from gl.fixed_point import fixed_point, substitute
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl

@st.composite
def modalized_formulas(draw, max_depth=3):
    base_p = Box(draw(st.sampled_from([
        atom("p"), 
        Not(atom("p")), 
        Imp(atom("p"), atom("q")), 
        Box(atom("p"))
    ])))
    
    def build_expr(depth):
        if depth == 0:
            return draw(st.sampled_from([base_p, atom("q"), bot()]))
        op = draw(st.sampled_from(["not", "and", "or", "imp", "iff", "box"]))
        if op == "not": return Not(build_expr(depth - 1))
        elif op == "box": return Box(build_expr(depth - 1))
        elif op == "and": return And(build_expr(depth - 1), build_expr(depth - 1))
        elif op == "or": return Or(build_expr(depth - 1), build_expr(depth - 1))
        elif op == "imp": return Imp(build_expr(depth - 1), build_expr(depth - 1))
        elif op == "iff": return Iff(build_expr(depth - 1), build_expr(depth - 1))
            
    return build_expr(max_depth)

@settings(max_examples=200, deadline=None)  # ≥ 200 件の要求を満たす規模
@given(modalized_formulas())
def test_random_fixed_points(A):
    if not is_modalized_in(A, "p"):
        return
    H = fixed_point(A, "p")
    fp_equation = Iff(H, substitute(A, "p", H))
    assert prove_gl(fp_equation).status == "proved"