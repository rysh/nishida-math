from gl.formula import Formula, Not, And, Or, Imp, Iff, Box, bot, atoms
from gl.modalized import is_modalized_in

def substitute(formula: Formula, var: str, replacement: Formula) -> Formula:
    """formula の中の atom `var` をすべて replacement で置換した式を返す。"""
    if formula.type == "atom":
        return replacement if formula.name == var else formula
    elif formula.type == "bot":
        return formula
    elif formula.type == "not":
        return Not(substitute(formula.arg, var, replacement))
    elif formula.type == "and":
        return And(*(substitute(arg, var, replacement) for arg in formula.args))
    elif formula.type == "or":
        return Or(*(substitute(arg, var, replacement) for arg in formula.args))
    elif formula.type == "imp":
        return Imp(substitute(formula.left, var, replacement), substitute(formula.right, var, replacement))
    elif formula.type == "iff":
        return Iff(substitute(formula.left, var, replacement), substitute(formula.right, var, replacement))
    elif formula.type == "box":
        return Box(substitute(formula.arg, var, replacement))
    return formula

def substitute_formula(formula: Formula, target: Formula, replacement: Formula) -> Formula:
    """formula 内の部分式 target を完全に replacement に置換する。"""
    if formula == target:
        return replacement
    if formula.type in ("atom", "bot"):
        return formula
    elif formula.type == "not":
        return Not(substitute_formula(formula.arg, target, replacement))
    elif formula.type == "and":
        return And(*(substitute_formula(arg, target, replacement) for arg in formula.args))
    elif formula.type == "or":
        return Or(*(substitute_formula(arg, target, replacement) for arg in formula.args))
    elif formula.type == "imp":
        return Imp(substitute_formula(formula.left, target, replacement), substitute_formula(formula.right, target, replacement))
    elif formula.type == "iff":
        return Iff(substitute_formula(formula.left, target, replacement), substitute(formula.right, target, replacement))
    elif formula.type == "box":
        return Box(substitute_formula(formula.arg, target, replacement))
    return formula

def get_top_boxes(A: Formula, p: str) -> list[Formula]:
    """A の中で p を含む最上位（他の Box に包まれていない）Box 部分式のリストを返す。"""
    boxes = []
    def visit(formula: Formula):
        if formula.type == "box":
            if p in atoms(formula):
                if formula not in boxes:
                    boxes.append(formula)
                return
        elif formula.type == "not":
            visit(formula.arg)
        elif formula.type in ("and", "or"):
            for arg in formula.args:
                visit(arg)
        elif formula.type in ("imp", "iff"):
            visit(formula.left)
            visit(formula.right)
    visit(A)
    return boxes

def fixed_point(A: Formula, p: str) -> Formula:
    """
    A において p が □ 下にのみ出現するときに H を返す。
    GL ⊢ H ↔ A[p := H]
    """
    if not is_modalized_in(A, p):
        raise ValueError(f"Variable '{p}' is not strictly modalized in {A}")
    
    if p not in atoms(A):
        return A
    
    top_boxes = get_top_boxes(A, p)
    D_map = {}
    
    for T in top_boxes:
        B = T.arg
        # T を ⊤ (Not(bot())) に置換して部分問題を解く
        A_T = substitute_formula(A, T, Not(bot()))
        fp_A_T = fixed_point(A_T, p)
        # 導出された固定点を箱の中の p に代入する
        D = Box(substitute(B, p, fp_A_T))
        D_map[T] = D
        
    H = A
    for T, D in D_map.items():
        H = substitute_formula(H, T, D)
        
    return H