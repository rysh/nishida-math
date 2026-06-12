from gl.formula import Formula, Not, bot, atoms
from gl.modalized import is_modalized_in
from gl.fixed_point import substitute, substitute_formula, get_top_boxes

def fixed_point(A: Formula, p: str) -> Formula:
    """
    代替実装：De Jongh-Sambin の Direct Substitution アルゴリズム。
    A 内の p を含む最上位 Box をすべて ⊤ に置換した式 A_top を作成し、
    元の A の p をすべて A_top に一括置換する。
    """
    if not is_modalized_in(A, p):
        raise ValueError(f"Variable '{p}' is not strictly modalized in {A}")
        
    if p not in atoms(A):
        return A
        
    top_boxes = get_top_boxes(A, p)
    A_top = A
    
    # すべての最上位 Box を ⊤ に置換
    for T in top_boxes:
        A_top = substitute_formula(A_top, T, Not(bot()))
        
    # p を A_top で置換する
    return substitute(A, p, A_top)