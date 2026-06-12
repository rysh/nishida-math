"""
src/gl/modalized.py
静的検査：p が A 内で □ の下にのみ出現するか
（engine 内部で prover を呼ばない）
"""
from gl.formula import Formula
from typing import Any

def is_modalized_in(A: Formula, p: str) -> bool:
    """pがA内で□の下にのみ出現するか（自由出現はない）"""
    def check(f: Formula, under_box: bool) -> bool:
        if f.type == "atom":
            if f.name == p:
                return under_box
            return True
        if f.type == "bot":
            return True
        if f.type == "not":
            return check(f.arg, under_box)
        if f.type in ("and", "or"):
            return all(check(arg, under_box) for arg in f.args)
        if f.type in ("imp", "iff"):
            return check(f.left, under_box) and check(f.right, under_box)
        if f.type == "box":
            return check(f.arg, True)  # □ 下に入る
        return True
    return check(A, False)
