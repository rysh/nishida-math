from gl.formula import Formula, Not, Box, bot, atoms
from gl.modalized import is_modalized_in
from gl.fixed_point import substitute, substitute_formula, get_top_boxes

def fixed_point(A: Formula, p: str) -> Formula:
    """代替実装: ループ駆動型プレースホルダー順次解消アルゴリズム（非再帰）"""
    if not is_modalized_in(A, p):
        raise ValueError(f"Variable '{p}' is not strictly modalized in {A}")
        
    if p not in atoms(A):
        return A
        
    top_boxes = get_top_boxes(A, p)
    resolved_substitutions = {}
    
    # 再帰を使わず、ループで各最上位Boxの局所解をプレースホルダーを用いて反復解消
    for T in top_boxes:
        local_A_top = A
        for other_T in top_boxes:
            if other_T != T:
                local_A_top = substitute_formula(local_A_top, other_T, Not(bot()))
        
        local_A_top = substitute_formula(local_A_top, T, Not(bot()))
        resolved_substitutions[T] = Box(substitute(T.arg, p, local_A_top))
        
    H = A
    for T, replacement in resolved_substitutions.items():
        H = substitute_formula(H, T, replacement)
        
    return H