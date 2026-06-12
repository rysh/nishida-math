# 案 Gemini — T2 固定点エンジン

## 0. 自己申告（必須・先頭に置く）

* 確信度：High
* 不安な箇所（具体的に、最低 3 つ）：
1. `hypothesis` によるランダムテスト生成において、`p` が modalized された式を効率よく生成する strategy のパフォーマンス（棄却率が高くなりすぎないよう、構成的に生成するアプローチを採用しました）。
2. 深くネストされた `Box` の中にある `p` に対して、De Jongh-Sambin の直接置換（代替アルゴリズム）が、GL 証明器の計算量爆発を引き起こさないか。
3. Python の再帰制限（非常に深い式が生成された場合）。ただし `hypothesis` の `max_leaves` を制限することで回避しています。


* 参照した文献・URL（あれば）：
* Boolos, G. (1993). *The Logic of Provability*. (Chapter 8: The Fixed Point Theorem)
* Smoryński, C. (1985). *Self-Reference and Modal Logic*.
* Sambin, G. (1976). *An effective fixed-point theorem in intuitionistic diagonalizable algebras*.


* ハルシネーション可能性が高い記述：
* 哲学的な主張や歴史的経緯（西田とGödelの結びつきなど）については、証明された事実ではなく「illustration」としての位置づけを徹底しています。


* **特別申告**：
* Boolos 1993 の第8章、および Smoryński のアルゴリズムを過去の学習データから正確に再構成しました。
* 実装した主アルゴリズム（Recursive Sambin/Boolos 法）と代替アルゴリズム（De Jongh-Sambin 直接置換法）の対応関係についての確信度は非常に高いです。両者は構文的には異なる文字列を生成しますが、GL ⊢ で同値になることが数学的に保証されています。



---

## 1. 設計判断（散文、簡潔に）

固定点定理（$GL \vdash H \leftrightarrow A(H)$）の構成的証明には、主に2つのアルゴリズムが知られています。
本実装では、これら2つを別々に実装し、独立した GL 証明器で同値性を検証させる強力な Differential Testing の構成としました。

1. **主アルゴリズム（Recursive Sambin / Boolos法）**:
式 $A(p)$ の中から $p$ を含む「最上位の $\Box$ 式（$T_i$）」を抽出し、それぞれの $T_i$ を $\top$ に置き換えた縮小系に対して再帰的に固定点を求め、その結果を元の箱の中に代入して $D_i$ を構築します。最後に元の式の $T_i$ を $D_i$ に置換します。Boolos (1993) の証明に沿った、最も標準的で式が爆発しにくいアプローチです。
2. **代替アルゴリズム（De Jongh-Sambin 直接置換法）**:
$A(p)$ の中の $p$ を含む最上位の $\Box$ 式を**すべて同時に** $\top$ で置き換えた純粋な命題論理式 $A^\top$ を作り、元の $A(p)$ の中の $p$ をすべて $A^\top$ に一括置換する手法です。驚くべきことに、GLの枠組み（Löbの定理とK4）では、この単純な $O(N)$ の一括置換だけで正しい固定点が得られます。

これらは Engine 内部で完結しており、外部の `gl.tableau` や `gl.kripke_search` は一切 import しません。正しさの判定はすべて `tests/` 側に委譲しています。

---

## 2. 疑似コード（言語非依存）

```text
// Main Algorithm (Recursive Sambin / Boolos)
function fixed_point(A, p):
    if p not in A:
        return A
    
    top_boxes = get_maximal_box_subformulas_containing(A, p)
    D_map = empty dictionary
    
    for T in top_boxes:  // T is of the form Box(B)
        A_T = replace_subformula(A, T, Top)
        fp_A_T = fixed_point(A_T, p)  // Recursive solving
        D = Box( replace_variable(T.arg, p, fp_A_T) )
        D_map[T] = D
        
    H = A
    for T, D in D_map:
        H = replace_subformula(H, T, D)
        
    return H

// Alternative Algorithm (De Jongh-Sambin Direct Substitution)
function fixed_point_alt(A, p):
    if p not in A:
        return A
        
    top_boxes = get_maximal_box_subformulas_containing(A, p)
    A_top = A
    for T in top_boxes:
        A_top = replace_subformula(A_top, T, Top)
        
    return replace_variable(A, p, A_top)

```

---

## 3. Python 実装（モジュール単位）

### `src/gl/modalized.py`

静的検査用モジュール。

```python
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

```

### `src/gl/fixed_point.py`

主アルゴリズム（再帰的構築）。外部 prover には一切依存しません。

```python
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

```

### `src/gl/fixed_point_alt.py`

代替アルゴリズム（De Jongh-Sambin ダイレクト置換）。

```python
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

```

---

## 4. テスト（pytest 形式）

独立検証器 `gl.tableau.prove_gl` を用いて検証します。

### `tests/test_fixed_point_kats.py`

```python
import pytest
from gl.formula import atom, bot, Not, Box, Imp, Iff
from gl.fixed_point import fixed_point, substitute
from gl.tableau import prove_gl

def assert_fixed_point(A, p, expected_H):
    """
    独立 prover を用いて、
    1. 生成された H が expected_H と GL 同値であること
    2. GL ⊢ H ↔ A[p:=H] が成立すること
    を検証する。
    """
    H = fixed_point(A, p)
    
    # 1. 期待される式との同値性チェック
    equiv_to_expected = Iff(H, expected_H)
    assert prove_gl(equiv_to_expected).status == "proved", \
        f"H not GL-equivalent to expected: {H} vs {expected_H}"
        
    # 2. 固定点方程式のチェック
    fp_equation = Iff(H, substitute(A, p, H))
    assert prove_gl(fp_equation).status == "proved", \
        f"GL ⊬ H ↔ A[p:=H]: H={H}"

def test_godel_fixed_point():
    """
    KAT 1: A(p) = ¬□p -> H = ¬□⊥ (Gödel sentence)
    H ↔ ¬□H は □⊥ ↔ □¬□⊥ に帰着。
    (→): □単調性。
    (←): ¬□⊥ ≡ (□⊥→⊥), ∴ □¬□⊥ ≡ □(□⊥→⊥), Löb により □⊥.
    """
    A = Not(Box(atom("p")))
    assert_fixed_point(A, "p", Not(Box(bot())))

def test_henkin_fixed_point():
    """KAT 2: A(p) = □p -> H = ⊤"""
    A = Box(atom("p"))
    assert_fixed_point(A, "p", Not(bot()))

def test_lob_fixed_point():
    """KAT 3: A(p) = □p → q -> H = □q → q"""
    A = Imp(Box(atom("p")), atom("q"))
    assert_fixed_point(A, "p", Imp(Box(atom("q")), atom("q")))

def test_lob_instance_fixed_point():
    """KAT 4: A(p) = □¬p -> H = □⊥"""
    A = Box(Not(atom("p")))
    assert_fixed_point(A, "p", Box(bot()))

```

### `tests/test_fixed_point_random.py`

```python
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

```

### `tests/test_fixed_point_uniqueness.py`

```python
import pytest
from hypothesis import given, settings
from gl.formula import Iff
from gl.fixed_point import fixed_point as fp_main
from gl.fixed_point_alt import fixed_point as fp_alt
from gl.tableau import prove_gl
from .test_fixed_point_random import modalized_formulas

@settings(max_examples=50, deadline=None)
@given(modalized_formulas(max_depth=2))
def test_two_algorithms_equivalence(A):
    """
    主アルゴリズムと代替アルゴリズムが出力する H1 と H2 が、
    構文的には異なっても GL において証明論的に同値であることを検証する。
    """
    H1 = fp_main(A, "p")
    H2 = fp_alt(A, "p")
    
    equiv = Iff(H1, H2)
    assert prove_gl(equiv).status == "proved", f"Algorithms diverged for {A}:\nMain: {H1}\nAlt: {H2}"

```

---

## 5. 自分の実装をデバッグする手順

1. `test_fixed_point_kats.py` を実行し、既知の4パターンに対して構文レベルに近い形で期待通りの H が生成されているかを確認します。
2. もし KAT が `proved` にならない場合、`fixed_point.py` の `substitute_formula` が部分式（例: `Box(p)`）を正確にターゲティングして置換できているか（参照同一性ではなく値の同一性で比較しているか）をチェックします。
3. `test_two_algorithms_equivalence.py` が落ちた場合、両アルゴリズムの出力を print し、手動でタブロー証明器を走らせてどちらが不正な固定点（または反例モデル）を生成しているかを特定します。

---

## 6. 既知の限界・未実装

* **構文木の正規化（NNF/DNF）の欠如**: 処理の前に事前最適化を行っていないため、不必要に冗長な $H$ が生成される可能性があります。
* **計算量**: 深いネストを持つ式に対して、アルゴリズムが生成する $H$ のサイズは指数的に増大する可能性があります（ただし、GLの枠組みでは等価なより短い式が存在します）。
* 静的検査 `is_modalized_in` は、式の中に束縛変数の概念がない命題論理前提で記述されています（これは仕様通りです）。

---

## 7. 他案と差分が出そうなポイント（予想 3 つ）

1. **ベースアルゴリズムの選択**: 私は Boolos (1993) / Sambin (1976) のトップダウン・再帰置換法を主とし、De Jongh-Sambin のダイレクト一括置換（$H = A[p \mapsto A^\top]$）を代替案としました。他 LLM は、単純な反復置換 $H_{k+1} = A(H_k)$ を実装し、それが GL 上で収束することをアテにするかもしれません（これは構文レベルでは無限ループや発振を起こすリスクがあります）。
2. **`is_modalized_in` の実装の堅牢性**: 変数 $p$ が $\Box$ の下にあるかどうかの深さをトラッキングする際、AST の再帰下降で `in_box` フラグを伝播させる方式を取りました。他案は `atoms(A)` から場当たり的にチェックする可能性があります。
3. **`tests/` 側への依存分離の徹底**: 仕様指示の通り、`fixed_point*.py` 内に `prove_gl` の呼び出しや、`status == "proved"` などの検査ロジックを一切含めていません。すべて独立したテストモジュール側でのみ Tableau/Kripke prover を実行しています。