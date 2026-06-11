# S1 送信用合体プロンプト

> このファイルは、S1（LP / 古典命題論理の評価器 = WP4）を **ChatGPT GPT-5 or o3** に
> 投げるための合体プロンプトです。下のセクション（区切り線で囲まれた部分）を
> **そのままコピペ** して新規スレッドで送ってください。
>
> 戻ってきた成果物は `incoming/S1_lp_classical_evaluator/chatgpt.md`
> （または zip）に置いてください。

---

> あなたは「ケーテル西田 / Generative Contradiction」プロジェクトの計算的展示を作るための
> **補助エージェント**です。あなたの出力はそのまま採用されません。Claude Code が読み、
> 必要に応じて他 LLM の出力と差分統合します。あなたの責務は「最善を尽くす」だけでなく、
> **どこに不確かさがあるかを正直に申告する**ことを含みます。
>
> ## プロジェクトの骨子
>
> Nishida Kitarō の絶対矛盾的自己同一と Gödel 不完全性が同じ **productive self-reference**
> 構造を記述している、という哲学的主張の **illustration**（証明ではない）を、
> 機械検証された artifacts として作る。
>
> 同じ自己言及種を 3 環境に植える：
>
> 1. **古典命題論理** — λ ↔ ¬λ は充足不可能 → 爆発
> 2. **LP（Priest, 3 値）** — v(λ)=b で充足。λ-free 言語では何も新しく従わない（inert）
> 3. **GL（Gödel–Löb 証明可能性論理）** — Gödel 型固定点 H ↔ ¬□H が ¬□⊥ ≡ Con に解け、
>    Con₀ ⊊ Con₁ ⊊ Con₂ ⊊ … の厳密無限階層を launch（generation）
>
> ## 不変式（破ったら不採用）
>
> - 出力するコード・主張・文章は、Claude Code 側の検証パイプラインで
>   機械検証されて初めて採用される。
> - すべての claim は計算的に検証可能な形（テスト、列挙 artifact）で示す。
> - **禁止表現**：
>   1. シミュレーションが「哲学的テーゼを **証明する**」
>   2. 「西田が Gödel を **予見した**」（歴史的主張として）
>   3. 数学的内容に対する **新規性主張**（Solovay 1976, de Jongh–Sambin, Boolos 1993,
>      Priest 1979 等の既知の結果）
>   4. 因果消去主義的一般化
> - **引用語法**："consistent with / converges with / provides formal support for" を既定。
>   "building on / following" は西田と本論文著者にのみ用いる。
> - **認識論的位置づけ**：「illustration であって proof ではない」を明示。
>
> ## 共有データ形式
>
> **Formula JSON**：
> ```json
> {"type":"bot"} | {"type":"atom","name":"p"} | {"type":"not","arg":F}
> | {"type":"and","args":[F,...]} | {"type":"or","args":[F,...]}
> | {"type":"imp","left":F,"right":F} | {"type":"iff","left":F,"right":F}
> | {"type":"box","arg":F}
> ```
>
> **言語**：Python 3.12（`uv` 管理）。純粋関数中心。
> **テスト**：`pytest` + `hypothesis`。仕様が変わったらテストも変える（テストが従うのは仕様）。

---

## タスク

指示書 §2.4 の **LP（Priest's Logic of Paradox）** と **古典命題論理** の評価器を
Python 3.12 で実装し、指示書 E-B1, E-B2 の実験を走らせてください。

### LP の定義

- 値：{t, b, f}、順序 f < b < t
- 指定値（designated）：{t, b}
- ¬(t)=f, ¬(b)=b, ¬(f)=t
- ∧ = min, ∨ = max
- A → B := ¬A ∨ B
- A ↔ B := (A → B) ∧ (B → A)
- Γ ⊨_LP φ ⇔ Γ をすべて指定する任意 valuation が φ も指定

### 古典命題論理

- LP の値 {t, f} 制限版（同じ機械）
- 比較のため同じインターフェイスで実装

### 仕様

```python
# Lit は 't' | 'b' | 'f' を表す型
def evaluate_lp(formula: Formula, valuation: dict[str, Lit]) -> Lit:
    """formula に □ (type='box') が含まれていたら ValueError"""

def entails_lp(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool:
    """3^|atoms| 通り総当たり"""

def evaluate_classical(formula: Formula, valuation: dict[str, bool]) -> bool: ...
def entails_classical(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool: ...
```

### E-B1 古典爆発展示

- λ ↔ ¬λ は古典で充足不可能 → 列挙 artifact
- 任意 B について λ↔¬λ ⊨_cl B（vacuous）の確認
- 出力 JSON：`{"satisfiable": false, "vacuous_explosion": true, "enumeration_size": int}`

### E-B2 LP quarantine 展示

- 充足性：v(λ)=b で λ↔¬λ が指定値 → valuation artifact
- **保存性（inertness）補題**：λ-free B について
  `T, λ∧¬λ ⊨_LP B ⇔ T ⊨_LP B`
  - 原子変数 ≤ 4（3^4 = 81 valuation、総当たり）
  - 任意の小 T と λ-free B で双方向確認
- **MP 失敗**：A, A→B ⊭_LP B、witness valuation を出力（v(A)=b, v(B)=f）
- **DS 失敗**：A∨B, ¬A ⊭_LP B、同様
- 出力 JSON：`{"satisfiable": true, "inert": true, "mp_failure": valuation, "ds_failure": valuation}`

### KAT

- 古典：λ↔¬λ が 2 valuation すべてで f
- LP：v(λ)=b で λ↔¬λ の値が b（指定）
- inertness：λ-free 言語 4 atoms 完全列挙で違反ゼロ

### 提出物

1. `src/lp/evaluator.py`
2. `src/lp/entailment.py`
3. `src/classical/evaluator.py`
4. `src/classical/entailment.py`
5. `experiments/wp4/e_b1_classical_explosion.py`
6. `experiments/wp4/e_b2_lp_quarantine.py`
7. `experiments/wp4/artifacts/`（出力 JSON）
8. `tests/test_lp.py`、`tests/test_classical.py`

### 注意

- formula 型は GL と共通。**`src/gl/formula.py` から `Formula`, `bot`, `atom`,
  `Not`, `And`, `Or`, `Imp`, `Iff` を import** して使うこと。重複定義禁止。
- `Box` も同モジュールにあるが、LP / 古典では `type == "box"` を見つけたら `ValueError` を投げて拒否
- 純粋関数中心（dict は不変として扱う、再代入で更新する場合も新規辞書を作る）

---

## 既存の Formula 型の実物（src/gl/formula.py、必ずこれを import）

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, TypeAlias

FormulaJSON: TypeAlias = dict[str, Any]


@dataclass(frozen=True, slots=True)
class Formula:
    type: str
    name: str | None = None
    arg: "Formula | None" = None
    args: tuple["Formula", ...] = ()
    left: "Formula | None" = None
    right: "Formula | None" = None

    def to_json(self) -> FormulaJSON: ...
    @staticmethod
    def from_json(data: Mapping[str, Any]) -> "Formula": ...


# コンストラクタ関数
def bot() -> Formula: ...
def atom(name: str) -> Formula: ...
def Not(arg: Formula) -> Formula: ...
def And(*args: Formula) -> Formula: ...
def Or(*args: Formula) -> Formula: ...
def Imp(left: Formula, right: Formula) -> Formula: ...
def Iff(left: Formula, right: Formula) -> Formula: ...
def Box(arg: Formula) -> Formula: ...  # LP/古典では拒否対象


# 既存ヘルパ
def atoms(f: Formula) -> frozenset[str]: ...   # 出現原子の集合（boxも含めて再帰）
def subformulas(f: Formula) -> frozenset[Formula]: ...
def modal_depth(f: Formula) -> int: ...
def pretty(f: Formula) -> str: ...
```

使用例：
```python
from gl.formula import Formula, bot, atom, Not, And, Or, Imp, Iff

p = atom("p")
liar = Iff(atom("lambda"), Not(atom("lambda")))   # λ ↔ ¬λ
expr = And(p, Not(p))                              # p ∧ ¬p
```

## 既存リポジトリ構成（参考）

```
src/
├── gl/
│   ├── __init__.py
│   ├── formula.py             ← import 対象
│   ├── tableau.py
│   ├── kripke_search.py
│   └── countermodel_verifier.py
└── lp/                        ← あなたが新規作成
└── classical/                 ← あなたが新規作成
tests/
├── test_gl_kats.py            ← 既存、変更不要
├── test_gl_random.py          ← 既存、変更不要
├── test_lp.py                 ← あなたが新規作成
└── test_classical.py          ← あなたが新規作成
experiments/wp4/               ← あなたが新規作成
pyproject.toml                 ← 必要なら追記提案だけ。私が反映する。
```

## §0 自己申告（必須・先頭に置く）

成果物の冒頭に、以下を明記してください：

- 確信度：High / Medium / Low（このタスク全体について）
- 不安な箇所（具体的に、最低 3 つ）
- 参照した文献・URL（あれば）
- ハルシネーション可能性が高い記述（自分で気付いたもの）

たとえば：
- LP の `→` 定義は ¬A∨B で正しいか？（実装で常に確認）
- inertness lemma の λ-free B のスコープに含めるべき式の範囲（任意のサイズ？深さ制限？）
- MP/DS 失敗 witness の最小性

## 出力形式

- 各 Python ファイルを fenced code block で
- ファイル名を block 冒頭にコメントで明示
- pytest が `uv run pytest -q` で通ることを自分のローカルで確認
- 通った件数を本文末尾に書いてください（例：`X passed`）
