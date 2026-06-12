"""
tests/test_fixed_point_random.py
Random Battery（≥200件目標）
- hypothesis で modalized な A(p) を生成（depth ≤ 3, 余分原子 ≤ 2）
- 生成時点で is_modalized_in で filter
- 各々で H を計算 → 独立 prover (tableau) で GL ⊢ H ↔ A[p:=H] を検証
- 失敗は hypothesis の shrink で最小化して報告
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
# 注意: 実際のプロジェクトでは既存の Formula 生成 strategy を import して使う
# ここでは簡易版としてランダムテストの骨組みのみ提供（統合時に拡張）

from gl.formula import atom, bot, Not, Box, Imp, And, Or, Iff
from gl.fixed_point import fixed_point, substitute
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl


def simple_modalized_formula_strategy():
    """簡易的な modalized formula 生成（実プロジェクトではより洗練された strategy に置換）"""
    # 実装は既存リポジトリの formula 生成ロジックに依存するため省略
    # ここでは pytest でスキップし、統合時に本格実装することを推奨
    return st.just(Not(Box(atom("p"))))  # ダミー（実際は複雑な strategy）


@settings(max_examples=50, deadline=None)  # 200件目標は統合時に max_examples=250 以上に
@given(A=simple_modalized_formula_strategy())
def test_random_modalized_fixed_point(A):
    p = "p"
    assume(is_modalized_in(A, p))
    H = fixed_point(A, p)
    fp_equation = Iff(H, substitute(A, p, H))
    result = prove_gl(fp_equation)
    assert result.status == "proved", f"Random case failed: A={A}, H={H}"
