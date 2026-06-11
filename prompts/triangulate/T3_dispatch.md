# T3 送信用合体プロンプト（Con_n 帰納証明 / 3 LLM 並走）

> このファイルは、T3（Con_n ≡ ¬□^{n+1}⊥ の帰納証明 = WP3 の一部）を
> **ChatGPT / Grok / Gemini に独立に同一文** で投げるための合体プロンプトです。
> 下のセクション（区切り線で囲まれた部分）を **そのままコピペ** して、
> 3 つの新規スレッドそれぞれに送ってください。
>
> 戻ってきた成果物はそれぞれ：
> - `incoming/T3_con_n_induction/chatgpt.md`（or zip）
> - `incoming/T3_con_n_induction/grok.md`（or zip）
> - `incoming/T3_con_n_induction/gemini.md`（or zip）

---

> あなたは「ケーテル西田 / Generative Contradiction」プロジェクトの計算的展示を作るための
> **補助エージェント**です。あなたの出力はそのまま採用されません。**3 つの独立した LLM
> （ChatGPT / Grok / Gemini）から同じ問題に対する案を集め、Claude Code が差分比較して
> いいとこ取りで統合**します。よってあなたの責務は「最善を尽くす」だけでなく、
> **どこに不確かさがあるかを正直に申告する**ことを含みます。
>
> ## プロジェクトの骨子
>
> Nishida Kitarō の絶対矛盾的自己同一と Gödel 不完全性が同じ **productive self-reference**
> 構造を記述している、という哲学的主張の **illustration**（証明ではない）。
> Con₀ ⊊ Con₁ ⊊ Con₂ ⊊ … の厳密無限階層を GL レベルで機械検証する。
>
> ## 不変式（破ったら不採用）
>
> - すべての claim は GL 証明器で機械検証されて初めて採用される
> - **禁止表現**：哲学的テーゼの「証明」、Nishida の「予見」主張、数学的新規性主張、
>   因果消去主義的一般化
> - 引用語法："consistent with / converges with / provides formal support for"
>
> ## 既知の落とし穴（このタスク特有）
>
> - **Con_n のインデックス off-by-one**：Con_n ≡ ¬□^{n+1}⊥（**n+1 乗、n 乗ではない**）
> - **最小反例の世界数**：Con_n → Con_{n+1} の反例は線形 **(n+2)-鎖**（n+1 でも n+3 でもない）
> - 反射禁止と推移性の同時保持：反例モデル生成時、推移閉包を取った後で反射性が
>   壊れていないか毎回検査
> - 「□-単調性」と称して `A → B ⊢ □A → □B`（GL では成立）と
>   4 公理 `□A → □□A` を混同しない

---

## Triangulate 用：出力フォーマット強制

> あなたの出力は他の 2 つの LLM の出力と並べて diff されます。
> **以下のセクション構造を厳守**してください。

```
# 案 [あなたの自称名] — T3 Con_n 帰納証明

## 0. 自己申告（必須・先頭に置く）

- 確信度：High / Medium / Low
- 不安な箇所（具体的に、最低 3 つ）：
- 参照した文献・URL（あれば）：
- ハルシネーション可能性が高い記述：
- **特別申告**：
  - off-by-one を自分が踏みうる箇所を最低 5 つ列挙
  - 紙の証明で一度書いた後に書き直した箇所があれば before/after

## 1. 紙の証明（Markdown 数式、厳密に）
## 2. テストコード（pytest）
## 3. (Monotone) Con_{n+1} → Con_n の証明と機械検証
## 4. (Strict) Con_n → Con_{n+1} の反例モデル
## 5. 自分の実装をデバッグする手順
## 6. 既知の限界・未実装
## 7. 他案と差分が出そうなポイント（予想 3 つ）
```

---

## タスク

指示書 §2.3 の主張：

> Con_0 := ¬□⊥
> Con_{n+1} := ¬□¬Con_n
>
> 定理：**Con_n ≡ ¬□^{n+1}⊥**

この帰納証明を **完全に厳密に** 書き、既存リポジトリの GL 証明器で n=0..8 を機械検証する
pytest コードを添えてください。さらに (Monotone) と (Strict) も機械検証してください。

### 既存リポジトリの実情（重要）

本プロジェクトには既に T1 で GL 証明器が統合されています。

```
src/gl/
├── formula.py             ← Formula 型と全コンストラクタ（後述）
├── tableau.py             ← prove_gl(formula) -> ProofResult（signed labelled tableau）
├── kripke_search.py       ← prove_gl(formula) -> ProofResult（finite Kripke search）
└── countermodel_verifier.py
tests/                     ← 既存テストは変更不要
pyproject.toml             ← pythonpath = ["src"]、testpaths = ["tests"]
experiments/wp3/           ← あなたが新規作成（反例モデル artifact）
docs/                      ← あなたが新規 docs/con_n_normal_form.md を追加
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
def box_power(arg: Formula, exponent: int) -> Formula   # □^n arg（**これを使うこと**）
def con(n: int) -> Formula                              # Con_n ≡ ¬□^{n+1}⊥（既存定義）
```

**注意**：`⊤` 単体のコンストラクタはありません。`Not(bot())` を使ってください。

### GL 証明器（既存、テストから import して使う）

```python
# from gl.tableau import prove_gl              # Method A（推奨）
# from gl.kripke_search import prove_gl        # Method B
# from gl.countermodel_verifier import verify_countermodel

def prove_gl(formula: Formula) -> ProofResult:
    """ProofResult.status は 'proved' | 'refuted'"""

def verify_countermodel(formula: Formula, model: dict) -> bool:
    """Kripke モデル JSON が formula を root(=0) で反証することを独立検証"""
```

### 要件

#### 1. 紙の証明（`docs/con_n_normal_form.md`）

- **Base case** n=0：Con_0 = ¬□⊥ ≡ ¬□^{0+1}⊥ ＝ ¬□^1⊥
- **Step**：Con_n ≡ ¬□^{n+1}⊥ を仮定して Con_{n+1} ≡ ¬□^{n+2}⊥ を示す
  - Con_{n+1} = ¬□¬Con_n
  - 仮定で ¬Con_n ≡ □^{n+1}⊥（**命題論理での否定取り**）
  - よって Con_{n+1} ≡ ¬□(□^{n+1}⊥) ＝ ¬□^{n+2}⊥
  - 各 step で **何を使ったか** を厳密に（命題的同値、□-単調性、Löb は使うか否か）

「命題的同値」と「GL-同値」の **区別** をつけること。¬Con_n と □^{n+1}⊥ の同値は
**命題論理的** に Con_n ≡ ¬□^{n+1}⊥ から従う（GL の □ 規則は使わない）。
ここを混ぜると証明全体が曖昧になる。

#### 2. 機械検証テストコード

```python
# tests/test_con_n_normal_form.py
import pytest
from gl.formula import bot, Box, Not, Iff, box_power
from gl.tableau import prove_gl

def Con(n: int):
    """Con_n の定義通り（再帰版）。既存の con(n) を使わず、定義式から組み立てる"""
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))

@pytest.mark.parametrize("n", range(9))
def test_con_n_normal_form(n: int):
    """Con_n ≡ ¬□^{n+1}⊥"""
    lhs = Con(n)
    rhs = Not(box_power(bot(), n + 1))
    result = prove_gl(Iff(lhs, rhs))
    assert result.status == "proved", \
        f"Con_{n} ≡ ¬□^{{{n+1}}}⊥ が GL で証明できない: {result}"
```

#### 3. (Monotone) Con_{n+1} → Con_n の機械検証

- 正規形を使って `¬□^{n+2}⊥ → ¬□^{n+1}⊥` を GL 証明器に渡す
- 対偶：`□^{n+1}⊥ → □^{n+2}⊥` ＝ □^{n+1}⊥ ⊢ □^{n+2}⊥ の 1 ステップ
- これは「□-単調性（A → B ⊢ □A → □B）」と **4 公理 □A → □□A** の区別が必要
- 紙の証明にこの区別を明示

```python
# tests/test_con_n_monotone.py
@pytest.mark.parametrize("n", range(9))
def test_con_monotone(n: int):
    """GL ⊢ Con_{n+1} → Con_n"""
    f = Imp(Con(n + 1), Con(n))
    assert prove_gl(f).status == "proved"
```

#### 4. (Strict) Con_n → Con_{n+1} の反例モデル

- 対象式：`Imp(Con(n), Con(n + 1))`
- 同値：`Imp(Not(box_power(bot(), n+1)), Not(box_power(bot(), n+2)))`
- 対偶：`box_power(bot(), n+2) → box_power(bot(), n+1)` を反証
- 最小反例：**線形 (n+2)-鎖**（root から終端まで n+2 個の世界、推移閉包込み）
  - n=0：worlds=[0,1]、rel=[[0,1]]
  - n=1：worlds=[0,1,2]、rel=[[0,1],[0,2],[1,2]]（推移閉包）
  - 一般：worlds=[0,1,...,n+1]、rel=推移閉包込みの完全順序
- root=0 で `□^{n+2}⊥` 成立、`□^{n+1}⊥` 不成立

各 n=0..4 について：

a. 反例モデル JSON を `experiments/wp3/countermodels/strict_n{0..4}.json` に出力
b. `verify_countermodel` で root において対象式を反証することを **独立検証**
c. さらに `prove_gl(Imp(Con(n), Con(n+1))).status == "refuted"` を確認

```python
# tests/test_con_n_strict.py
@pytest.mark.parametrize("n", range(5))
def test_con_strict_refutable(n: int):
    """GL ⊬ Con_n → Con_{n+1}"""
    f = Imp(Con(n), Con(n + 1))
    result = prove_gl(f)
    assert result.status == "refuted"
    assert result.countermodel is not None
    assert verify_countermodel(f, result.countermodel)

@pytest.mark.parametrize("n", range(5))
def test_minimal_countermodel_is_n_plus_2_chain(n: int):
    """最小反例 = 線形 (n+2)-鎖"""
    # experiments/wp3/countermodels/strict_n{n}.json を読んで
    # worlds が n+2 個、推移閉包が完全順序になっていることを確認
    ...
```

### 提出物

1. `docs/con_n_normal_form.md`（紙の証明、Markdown 数式）
2. `tests/test_con_n_normal_form.py`（n=0..8 機械検証）
3. `tests/test_con_n_monotone.py`（n=0..8）
4. `tests/test_con_n_strict.py`（n=0..4 + 反例モデル JSON 検証）
5. `experiments/wp3/countermodels/strict_n{0..4}.json`（5 個の artifact）
6. `experiments/wp3/build_countermodels.py`（artifact 生成スクリプト、純粋関数）

### このタスクで他案と差が出やすい論点（事前メモ）

- 帰納の step で命題論理的同値と GL 同値の境界をどこで引くか
- 4 公理（□A→□□A）の n 回適用の正確な書き下し（off-by-one の温床）
- 最小反例モデルの「線形 (n+2)-鎖」の世界数のカウント
- 反例モデル JSON の `rel` を推移閉包込みで書くか、生成側で閉包を取るか
- T1 prover の `prove_gl` が strict ケースで実際に refuted を返すかは prover の
  bound 設定次第（n=4 で深い chain が要る）。返さなければ `kripke_search.prove_gl` も
  試す、それでもダメなら **自分で構成した反例モデルを `verify_countermodel` で
  独立検証** する経路を必ず持つ

これらは §7 で必ず触れてください。

### 走らせ方

```bash
uv run pytest -q
```

成功確認後、本文末尾に通った件数を書いてください（例：`X passed`）。
