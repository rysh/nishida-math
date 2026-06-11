# T2 送信用合体プロンプト（固定点エンジン / 3 LLM 並走）

> このファイルは、T2（GL 固定点エンジン = WP2）を **ChatGPT / Grok / Gemini に独立に同一文** で
> 投げるための合体プロンプトです。下のセクション（区切り線で囲まれた部分）を
> **そのままコピペ** して、3 つの新規スレッドそれぞれに送ってください。
>
> 戻ってきた成果物はそれぞれ：
> - `incoming/T2_fixed_point/chatgpt.md`（or zip）
> - `incoming/T2_fixed_point/grok.md`（or zip）
> - `incoming/T2_fixed_point/gemini.md`（or zip）
>
> ## このタスクの最大のレビューポイント（Claude Code 用メモ、LLM には貼らない）
>
> **固定点エンジンの出力 H を、engine 自身のロジックで「正しい」と判定させないこと**。
> 必ず独立の GL 証明器（既存の `gl.tableau.prove_gl` または `gl.kripke_search.prove_gl`）で
> `GL ⊢ Iff(H, A.substitute(p, H))` を再検証する。指示書 §2.2 末尾と WP2 Definition of Done
> がこれを要求している。
>
> 3 案統合時に **engine と prover が同じ判定器を共有していないか** を最重点でチェックする。
> 危険信号：
> - `fixed_point.py` が独自の「H ↔ A(H) チェッカ」を持っていてそれが「pass」と言うので
>   テストも pass、と書かれているパターン
> - テストが `fixed_point` モジュール内の helper だけで「正しい」と確認しているパターン
> - import 構造で `fixed_point` が `tableau` / `kripke_search` を一切呼んでいないパターン
>
> 正しい構造：
> ```
>   tests/test_fixed_point_kats.py
>     ├── from gl.fixed_point import fixed_point
>     └── from gl.tableau import prove_gl  # 独立検証
>           ↓
>     H = fixed_point(A, "p")
>     equiv = Iff(H, A.substitute("p", H))
>     assert prove_gl(equiv).status == "proved"   # ← ここで独立検証
> ```

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
> 構造を記述している、という哲学的主張の **illustration**（証明ではない）を、
> 機械検証された artifacts として作る。
>
> ## 不変式（破ったら不採用）
>
> - 出力するコード・主張・文章は、本リポジトリの GL 証明器・反例モデル抽出器・LP 評価器で
>   機械検証されて初めて採用される。
> - すべての claim は「prover certificate」または「validated countermodel」を伴う。
> - **禁止表現**：
>   1. シミュレーションが「哲学的テーゼを **証明する**」
>   2. 「西田が Gödel を **予見した**」（歴史的主張として）
>   3. 数学的内容に対する **新規性主張**（既知の結果）
>   4. 因果消去主義的一般化
> - **引用語法**："consistent with / converges with / provides formal support for" を既定。
>   "building on / following" は西田と本論文著者にのみ用いる。
> - **認識論的位置づけ**：「illustration であって proof ではない」を明示。
>
> ## 既知の落とし穴（このタスク特有の自戒メモ）
>
> - **modalized 条件**：固定点定理の前提は「p が **□ の下にのみ** 出現」。これを忘れて
>   p の任意出現で再帰すると無限ループ／不正解。
> - **Löb 公理の適用方向**：□(□A→A) → □A であって、その逆ではない。
> - **Henkin の固定点**：□p の固定点は ⊤ であり、これは Löb の定理そのもの。
>   この自明性を忘れて「Henkin 文は ⊤ と同値ではない」と書く LLM が定期的にいる。
> - **「正しさ」の判定を engine 内で閉じない**：H が正しいかは engine 外の独立 prover が
>   GL ⊢ Iff(H, A.substitute(p, H)) を確認することで初めて決まる（後述）。

---

## Triangulate 用：出力フォーマット強制

> あなたの出力は他の 2 つの LLM の出力と並べて diff されます。
> **以下のセクション構造を厳守**してください。逸脱すると比較不能になります。

```
# 案 [あなたの自称名] — T2 固定点エンジン

## 0. 自己申告（必須・先頭に置く）

- 確信度：High / Medium / Low（このタスク全体について）
- 不安な箇所（具体的に、最低 3 つ）：
- 参照した文献・URL（あれば）：
- ハルシネーション可能性が高い記述：
- **特別申告**：
  - Boolos 1993 の該当章を本当に参照したか / 記憶を再構成したか / Web で参照したか
  - Boolos のアルゴリズム原文と自分の実装の対応関係についての確信度

## 1. 設計判断（散文、簡潔に）
## 2. 疑似コード（言語非依存）
## 3. Python 実装（モジュール単位）
## 4. テスト（pytest 形式）
## 5. 自分の実装をデバッグする手順
## 6. 既知の限界・未実装
## 7. 他案と差分が出そうなポイント（予想 3 つ）
```

---

## タスク

GL の **固定点定理**（de Jongh / Sambin, 1970s 中盤）の構成的アルゴリズムを Python 3.12 で
実装してください。

### 定理

任意のモーダル式 A(p) で **p が □ の下にのみ出現する**（modalized）とき、
GL ⊢ H ↔ A(H) を満たす H が A の他の変数のみから構成的に存在し、
GL-equivalence を除いて一意（Bernardi; de Jongh）。

実装参考：**Boolos, *The Logic of Provability* (1993)**（一次）；
Smoryński, *Self-Reference and Modal Logic* (1985)。

### 既存リポジトリの実情（重要）

本プロジェクトには既に T1 で GL 証明器が統合されています。あなたが書くコードは
これに乗っかります。

```
src/gl/
├── formula.py             ← Formula 型と全コンストラクタ（後述）
├── tableau.py             ← prove_gl(formula) -> ProofResult（signed labelled tableau）
├── kripke_search.py       ← prove_gl(formula) -> ProofResult（finite Kripke search）
└── countermodel_verifier.py
tests/
├── test_gl_kats.py        ← 既存、変更不要
└── test_gl_random.py      ← 既存、変更不要
pyproject.toml             ← pythonpath = ["src"]、testpaths = ["tests"]
```

### Formula 型（既存、絶対に重複定義しない）

```python
# from gl.formula import ...
@dataclass(frozen=True, slots=True)
class Formula:
    type: str           # "bot" | "atom" | "not" | "and" | "or" | "imp" | "iff" | "box"
    name: str | None = None
    arg: "Formula | None" = None
    args: tuple["Formula", ...] = ()
    left: "Formula | None" = None
    right: "Formula | None" = None
    def to_json(self) -> dict: ...
    @staticmethod
    def from_json(data) -> "Formula": ...

# コンストラクタ（これだけ import すれば十分）
def bot() -> Formula                        # ⊥
def atom(name: str) -> Formula
def Not(arg: Formula) -> Formula
def And(*args: Formula) -> Formula
def Or(*args: Formula) -> Formula
def Imp(left: Formula, right: Formula) -> Formula
def Iff(left: Formula, right: Formula) -> Formula
def Box(arg: Formula) -> Formula
def negate(arg: Formula) -> Formula         # 二重否定を消す簡略版
def box_power(arg: Formula, exponent: int) -> Formula   # □^n arg
def con(n: int) -> Formula                  # Con_n ≡ ¬□^{n+1}⊥
def atoms(f: Formula) -> frozenset[str]
def subformulas(f: Formula) -> frozenset[Formula]
def modal_depth(f: Formula) -> int
```

**注意**：`⊤` 単体のコンストラクタはありません。`Not(bot())` を使ってください。
このスキーマには `top` 型は存在しないので、出力 H 内に `⊤` が必要な場合（例：Henkin 固定点）は
`Not(bot())` を返してください。

### 既存 GL 証明器（必ずこれを独立検証に使う）

```python
# from gl.tableau import prove_gl as prove_gl_tableau
# from gl.kripke_search import prove_gl as prove_gl_kripke
# 両方とも：
def prove_gl(formula: Formula) -> ProofResult:
    """ProofResult.status は 'proved' | 'refuted'"""

@dataclass(frozen=True, slots=True)
class ProofResult:
    status: Literal["proved", "refuted"]
    certificate: dict | None = None
    countermodel: dict | None = None
```

### あなたが実装するもの

#### 仕様

```python
# src/gl/fixed_point.py
def fixed_point(A: Formula, p: str) -> Formula:
    """A において p が □ 下にのみ出現するときに H を返す。
    H は p を含まず GL ⊢ H ↔ A[p := H]。
    modalized でなければ ValueError。
    実装は engine 内部のロジックで完結し、GL 証明器の判定を呼ばないこと。
    （正しさの確認は外部の独立 prover の責任）"""

def substitute(formula: Formula, p: str, H: Formula) -> Formula:
    """formula の中の atom p をすべて H で置換した式を返す"""


# src/gl/modalized.py
def is_modalized_in(A: Formula, p: str) -> bool:
    """p が A 内で □ の下にのみ出現するか（自由出現はない）"""
```

#### **絶対要件：engine と prover を分離する**

固定点エンジン（`fixed_point.py`）の中で、出力 H の「正しさ」を engine 自身が判定しては
**ならない**。具体的には：

- `fixed_point` は `gl.tableau` / `gl.kripke_search` を import しない
- `fixed_point` 内部に「GL ⊢ ...」を判定する独自関数を持たない
- 「H ↔ A[p := H] が正しいか」のチェックは **テストコード側で** 行い、そこでだけ
  `gl.tableau.prove_gl` ないし `gl.kripke_search.prove_gl` を呼ぶ

これは指示書 §2.2 末尾の要件「The construction is effective ... For all other inputs the
engine computes H and the prover **verifies** GL ⊢ H ↔ A(H)」を実装に翻訳したものです。

#### Known-Answer Tests（必ず通す）

| 入力 A(p) | 期待 H |
|---|---|
| `Not(Box(atom("p")))` | `Not(Box(bot()))`（Gödel sentence ≡ Con） |
| `Box(atom("p"))` | `Not(bot())`（Henkin、Löb により inert）|
| `Imp(Box(atom("p")), atom("q"))` | `Imp(Box(atom("q")), atom("q"))`（Löb sentence）|
| `Box(Not(atom("p")))` | `Box(bot())`（Löb instance □(□⊥→⊥)→□⊥ で検証） |

各 KAT のテストは：

```python
# tests/test_fixed_point_kats.py
from gl.formula import atom, bot, Not, Box, Imp, Iff
from gl.fixed_point import fixed_point, substitute
from gl.tableau import prove_gl   # ← 独立検証用

def assert_fixed_point(A, p, expected_H):
    H = fixed_point(A, p)
    # 独立 prover で 2 つを検証
    equiv_to_expected = Iff(H, expected_H)
    assert prove_gl(equiv_to_expected).status == "proved", \
        f"H not GL-equivalent to expected: {H} vs {expected_H}"
    fp_equation = Iff(H, substitute(A, p, H))
    assert prove_gl(fp_equation).status == "proved", \
        f"GL ⊬ H ↔ A[p:=H]: H={H}"

def test_godel_fixed_point():
    A = Not(Box(atom("p")))
    assert_fixed_point(A, "p", Not(Box(bot())))
```

KAT 1（H = ¬□⊥）の検証手順（テスト docstring に書く）：
- H ↔ ¬□H は □⊥ ↔ □¬□⊥ に帰着
- (→)：□⊥ から □ 単調性
- (←)：¬□⊥ ≡ (□⊥→⊥)、∴ □¬□⊥ ≡ □(□⊥→⊥)、Löb (A:=⊥) で □(□⊥→⊥)→□⊥

#### Random Battery（≥ 200 件）

- モーダル深さ ≤ 3、余分原子変数 ≤ 2、modalized A(p) を 200 個以上 hypothesis で生成
- 各々 H を計算 → **独立 prover で** GL ⊢ Iff(H, substitute(A, p, H)) を検証
- 通らないものは hypothesis の shrink で最小化して報告
- p の出現が □ 下のみであることの静的検査 `is_modalized_in(A, p)` を strategy 側で
  filter として使う（生成後にチェックではなく、生成時点で modalized を保証）

#### 第 2 アルゴリズム（同一案内で別実装）

- Boolos アルゴリズムを 2 種類別ファイルで実装（簡易版でよい）：
  - `src/gl/fixed_point.py`（主）
  - `src/gl/fixed_point_alt.py`（代替、簡易でよい）
- 両出力 H₁, H₂ について `GL ⊢ Iff(H1, H2)` を独立 prover で検証
- 一致しなければ片方／両方バグ、報告

### 提出物

1. `src/gl/fixed_point.py`（主アルゴリズム、外部 prover を import しない）
2. `src/gl/fixed_point_alt.py`（代替実装、同様に prover を import しない）
3. `src/gl/modalized.py`（静的検査、prover を import しない）
4. `tests/test_fixed_point_kats.py`（独立 prover を呼んで KAT を検証）
5. `tests/test_fixed_point_random.py`（hypothesis、200 件以上）
6. `tests/test_fixed_point_uniqueness.py`（2 アルゴリズム一致、独立 prover で検証）

### このタスクで他案と差が出やすい論点（事前メモ）

- Boolos のアルゴリズムを **どの定式化で書くか**（substitution-based / Bernardi の
  uniqueness-経由 / Smoryński / Sambin のうちどれを基盤に？）
- modalized 性の静的検査の正確さ（出現位置の □-depth 追跡）
- A(p) の前処理（DNF / NNF 正規化）を入れるか
- 再帰の base case（A に p が出現しない場合）の扱い
- Löb の正方向 / 逆方向の適用判定

これらは §7 で必ず触れてください。

### 走らせ方

```bash
uv run pytest -q   # 既存 26 件 + あなたの新規分が全部通ること
```

成功確認後、本文末尾に通った件数を書いてください（例：`X passed`）。
