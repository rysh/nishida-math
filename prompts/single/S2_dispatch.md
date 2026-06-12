# S2 送信用合体プロンプト（Letterless 正規形 reducer / 単独 LLM）

> このファイルは、S2（Letterless 正規形 reducer = WP3 補助）を **ChatGPT GPT-5 or o3** に
> 投げるための合体プロンプトです。下のセクション（区切り線で囲まれた部分）を
> **そのままコピペ** して送ってください。
>
> 戻ってきた成果物は `incoming/S2_letterless_normal_form/chatgpt.md`（or zip）に置いてください。

---

> あなたは「ケーテル西田 / Generative Contradiction」プロジェクトの計算的展示を作るための
> **補助エージェント**です。あなたの出力はそのまま採用されません。Claude Code が読み、
> 必要に応じて他 LLM の出力と差分統合します。あなたの責務は「最善を尽くす」だけでなく、
> **どこに不確かさがあるかを正直に申告する**ことを含みます。
>
> ## プロジェクトの骨子
>
> Nishida Kitarō の絶対矛盾的自己同一と Gödel 不完全性が同じ **productive self-reference**
> 構造を記述している、という哲学的主張の **illustration**（証明ではない）。
> GL の letterless fragment（命題変数を含まない式）は □^n⊥ のブール結合に GL-同値で
> 一意に正規化できる（Boolos 1993 の Letterless Normal Form Theorem）。これを実装する。
>
> ## 不変式（破ったら不採用）
>
> - 出力するコード・主張・文章は、本リポジトリの GL 証明器で機械検証されて初めて採用される
> - **禁止表現**：哲学的テーゼの「証明」、Nishida の「予見」主張、数学的新規性主張、
>   因果消去主義的一般化
> - 引用語法："consistent with / converges with / provides formal support for"
> - 認識論的位置づけ：「illustration であって proof ではない」
>
> ## このタスク特有の注意
>
> **サイレント失敗リスク**：reducer が「正規形」と称して意味的に違う式を返すバグは
> 構文一致テストでは検出できない。**GL ⊢ input ↔ normal_form の機械検証を必ず併設** すること。

---

## タスク

GL の **letterless fragment**（命題変数を含まない式の集合）の **正規形 reducer** を実装する。

### 定理（Boolos 1993, Letterless Normal Form Theorem）

すべての letterless 式は □ⁿ⊥（n ≥ 0；□⁰⊥ = ⊥）のブール結合に GL-同値。
正規形は **□^n⊥ の有限集合のブール組み合わせ** として一意に表現可能。

### 既存リポジトリの実情

```
src/gl/
├── formula.py             ← Formula 型と全コンストラクタ（後述）
├── tableau.py             ← prove_gl(formula) -> ProofResult
├── kripke_search.py       ← prove_gl(formula) -> ProofResult
└── countermodel_verifier.py
tests/                     ← 既存テストは変更不要
pyproject.toml             ← pythonpath = ["src"]、testpaths = ["tests"]
```

### Formula 型（既存、絶対に重複定義しない）

```python
# from gl.formula import ...
def bot() -> Formula                          # ⊥
def atom(name: str) -> Formula
def Not(arg: Formula) -> Formula
def And(*args: Formula) -> Formula
def Or(*args: Formula) -> Formula
def Imp(left: Formula, right: Formula) -> Formula
def Iff(left: Formula, right: Formula) -> Formula
def Box(arg: Formula) -> Formula
def box_power(arg: Formula, exponent: int) -> Formula   # □^n arg
def atoms(f: Formula) -> frozenset[str]
def subformulas(f: Formula) -> frozenset[Formula]
def modal_depth(f: Formula) -> int
```

**注意**：`⊤` 単体のコンストラクタはありません。`Not(bot())` を使ってください。

### GL 証明器（テストで独立検証に使う、reducer 内では使わない）

```python
# from gl.tableau import prove_gl
# from gl.formula import Iff

def prove_gl(formula: Formula) -> ProofResult:
    """ProofResult.status は 'proved' | 'refuted'"""
```

### 仕様

```python
# src/gl/letterless.py

def is_letterless(F: Formula) -> bool:
    """F に atom 型ノードが一切ないか（type='atom' が再帰的に存在しない）"""

def letterless_normal_form(F: Formula) -> Formula:
    """letterless 式を正規形に変換した Formula を返す。
    正規形は box_power(bot(), n) のブール結合として表現。
    F が letterless でなければ ValueError。
    実装は内部だけで完結し、GL 証明器の判定を呼ばないこと
    （正しさの確認はテスト側の独立 prover の責任）"""

def nf_equiv(F1: Formula, F2: Formula) -> bool:
    """両方 letterless として正規形比較で GL-同値判定（構文一致ではない）。
    実装としては letterless_normal_form を両方に適用し、構文的に等しいかを
    Formula の to_json() で比較する。
    片方でも letterless でなければ ValueError"""
```

### 絶対要件：reducer と prover を分離する

`letterless.py` の中で、出力 normal form の「正しさ」を engine 自身が判定しては **ならない**：

- `letterless.py` は `gl.tableau` / `gl.kripke_search` を import しない
- 「GL ⊢ ...」の判定は **テストコード側** で `gl.tableau.prove_gl` を呼ぶ

### KAT（多めに、必ず通す）

各 KAT について、本リポジトリの `prove_gl` で
`GL ⊢ input ↔ letterless_normal_form(input)` を **必ず機械検証**。

| 入力 | 期待される正規形（GL-同値） |
|---|---|
| `bot()` | `box_power(bot(), 0)` ＝ `bot()` |
| `Not(bot())` | `Not(box_power(bot(), 0))` ＝ `Not(bot())` |
| `Box(bot())` | `box_power(bot(), 1)` |
| `Box(Box(bot()))` | `box_power(bot(), 2)` |
| `Not(Box(bot()))` | `Not(box_power(bot(), 1))`（≡ Con_0） |
| `Not(Box(Not(Box(bot()))))` | `Not(box_power(bot(), 1))`（≡ Con_0、Con_1 ではない：Löb instance による collapse — 内側 `Not(Box(bot))` ≡ `Imp(Box(bot), bot)`、ゆえに `Box(Not(Box(bot)))` ≡ `Box(Imp(Box(bot), bot))` ≡ `Box(bot)`） |
| `Not(Box(Box(bot())))` | `Not(box_power(bot(), 2))`（≡ Con_1） |
| `Or(Box(bot()), Not(Box(bot())))` | `Not(bot())`（GL ⊢ φ ∨ ¬φ） |
| `And(Box(bot()), Not(Box(bot())))` | `bot()` |
| `Box(Imp(Box(bot()), bot()))` | `box_power(bot(), 1)`（Löb instance：□(□⊥→⊥)→□⊥ で吸収） |
| `Box(Not(bot()))` | `Not(bot())`（GL ⊢ □⊤、つまり □(¬⊥) は定理） |

```python
# tests/test_letterless_kats.py
from gl.formula import bot, Box, Not, Or, And, Imp, Iff, box_power
from gl.tableau import prove_gl
from gl.letterless import letterless_normal_form

def check(input_f, expected_nf):
    nf = letterless_normal_form(input_f)
    # 構文一致は要求しない。GL-同値かを独立 prover で確認
    assert prove_gl(Iff(input_f, nf)).status == "proved", \
        f"input not GL-equivalent to its NF: {input_f} vs {nf}"
    assert prove_gl(Iff(nf, expected_nf)).status == "proved", \
        f"NF not GL-equivalent to expected: {nf} vs {expected_nf}"

def test_box_bot_reduces_to_box1_bot():
    check(Box(bot()), box_power(bot(), 1))
```

### Random Battery

- letterless 式を hypothesis でモーダル深さ ≤ 4 で 500 個生成
- 各々の正規形を計算 → `prove_gl(Iff(input, nf)).status == "proved"` を確認
- 違反は shrink で最小化して報告

### 提出物

1. `src/gl/letterless.py`（reducer、prover を import しない）
2. `tests/test_letterless_kats.py`（独立 prover で KAT 検証）
3. `tests/test_letterless_random.py`（hypothesis、500 件）

### よくあるバグ（事前警告）

- □⊤ を ⊤ に reduce 忘れ（GL ⊢ □⊤ の事実）
- Löb instance（□(□⊥→⊥) → □⊥）の吸収忘れ
- ブール結合の正規化（DNF 等）で構文一致を取ろうとして失敗
  → **構文一致ではなく GL-同値で判定** すること
- □^0⊥ と ⊥ の同一視忘れ

これらは KAT で全部潰せるので心配は要らないが、自分の実装でカバーしているか確認。

### §0 自己申告（必須・先頭に置く）

- 確信度：High / Medium / Low
- 不安な箇所（具体的に、最低 3 つ）：
- 参照した文献・URL（あれば）：
- ハルシネーション可能性が高い記述：
- **特別申告**：
  - Boolos 1993 の Letterless Normal Form Theorem 章を本当に参照したか
  - reduction 規則の正当性についての確信度

### 走らせ方

```bash
uv run pytest -q
```

成功確認後、本文末尾に通った件数を書いてください（例：`X passed`）。
