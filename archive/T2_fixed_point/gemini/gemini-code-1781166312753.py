import pytest
from hypothesis import given, settings, strategies as st
from gl.formula import atom, bot, Not, And, Or, Imp, Iff, Box, atoms
from gl.fixed_point import fixed_point, substitute
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl

# 構成的に modalized な式を生成する
@st.composite
def modalized_formulas(draw, max_depth=3):
    # p を含む式を Box で包んだものを基底とする
    base_p = Box(draw(st.sampled_from([
        atom("p"), 
        Not(atom("p")), 
        Imp(atom("p"), atom("q")), 
        Box(atom("p"))
    ])))
    
    # boolean combinations
    def build_expr(depth):
        if depth == 0:
            return draw(st.sampled_from([base_p, atom("q"), bot()]))
        
        op = draw(st.sampled_from(["not", "and", "or", "imp", "box"]))
        if op == "not":
            return Not(build_expr(depth - 1))
        elif op == "box":
            return Box(build_expr(depth - 1))
        elif op == "and":
            return And(build_expr(depth - 1), build_expr(depth - 1))
        elif op == "or":
            return Or(build_expr(depth - 1), build_expr(depth - 1))
        elif op == "imp":
            return Imp(build_expr(depth - 1), build_expr(depth - 1))
            
    formula = build_expr(max_depth)
    return formula

@settings(max_examples=200, deadline=None)
@given(modalized_formulas())
def test_random_fixed_points(A):
    # 事前条件のフィルタ（念のため）
    if not is_modalized_in(A, "p"):
        return
        
    H = fixed_point(A, "p")
    fp_equation = Iff(H, substitute(A, "p", H))
    
    result = prove_gl(fp_equation)
    assert result.status == "proved", f"Failed for A={A}, H={H}"