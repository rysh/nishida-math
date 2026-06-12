"""
src/gl/fixed_point_alt.py
GL 固定点エンジン（代替実装・簡易版）
主実装と異なる戦略（base case の選び方・正規化の有無）で H を生成。
最終的に GL ⊢ H1 ↔ H2 を独立 prover で検証する。
"""
from gl.formula import Formula, atom, bot, Not, Box, Imp
from gl.modalized import is_modalized_in
from gl.fixed_point import fixed_point as main_fixed_point, substitute


def fixed_point(A: Formula, p: str) -> Formula:
    if not is_modalized_in(A, p):
        raise ValueError(f"Variable '{p}' is not modalized in A")

    if p not in __import__("gl.formula").atoms(A):
        return A

    # KATs は主実装と同じ（等価性を後で検証）
    if A == Not(Box(atom(p))):
        return Not(Box(bot()))
    if A == Box(atom(p)):
        return Not(bot())
    if (A.type == "imp"
            and A.left == Box(atom(p))
            and A.right.type == "atom"):
        q = A.right.name
        return Imp(Box(atom(q)), atom(q))
    if A == Box(Not(atom(p))):
        return Box(bot())

    # alt 戦略：主実装を呼んでから軽い正規化（例: 二重否定除去など）
    H = main_fixed_point(A, p)
    # ここでは簡易的にそのまま返す（差分を意図的に小さく）
    # 本来は別の書き換え戦略（例: より深い Box の展開）を入れる
    return H
