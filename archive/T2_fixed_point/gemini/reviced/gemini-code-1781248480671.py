from gl.formula import Formula, atoms

def is_modalized_in(A: Formula, p: str) -> bool:
    """p が A 内で □ の下にのみ出現するか（自由出現はないか）を判定する。"""
    def check(formula: Formula, in_box: bool) -> bool:
        if formula.type == "atom":
            if formula.name == p:
                return in_box
            return True
        elif formula.type == "bot":
            return True
        elif formula.type == "not":
            return check(formula.arg, in_box)
        elif formula.type in ("and", "or"):
            return all(check(arg, in_box) for arg in formula.args)
        elif formula.type in ("imp", "iff"):
            return check(formula.left, in_box) and check(formula.right, in_box)
        elif formula.type == "box":
            return check(formula.arg, True)
        return True

    return check(A, False)