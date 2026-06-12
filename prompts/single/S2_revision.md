# S2 修正依頼（ChatGPT/Gemini 宛、同じスレッドで続けて貼る）

> ※ S2 は単独 LLM タスクですが、前回の提出は ChatGPT または Gemini 由来として
> Claude Code が受け取りました。同じスレッドで続けて貼ってください。

前回の S2 提出（letterless 正規形 reducer、interval/rank semantics 実装）を Claude Code がレビューしました。
**アルゴリズムは秀逸**（closed GL fragment の標準実装、`_box` の first-gap 計算が正確）です。
さらに **dispatch の KAT 表 6 行目のバグを発見して訂正したこと**は完璧な仕事でした
（`Not(Box(Not(Box(bot()))))` ≡ `Not(box_power(bot(), 1))` の方が正しい、と訂正してくれた件）。

統合前にやってほしいことが少しあります。

## 1. 実走確認（必須）

前回「リポジトリ本体と `gl.tableau.prove_gl` が手元にないため `X passed` を申告しない」と書いてくれましたね。
今回は実走してください。

リポジトリトップで：

```bash
uv run pytest -q
```

src tree：

```
src/gl/__init__.py             # 空
src/gl/formula.py              # Formula dataclass + bot, atom, Not, And, Or, Imp, Iff, Box,
                               # box_power, con, atoms, subformulas, modal_depth, pretty
                               # （全部 CamelCase）
src/gl/tableau.py              # prove_gl(formula: Formula) -> ProofResult
src/gl/kripke_search.py        # prove_gl(formula: Formula) -> ProofResult
src/gl/countermodel_verifier.py # verify_countermodel(formula, model_json) -> bool
```

`ProofResult.status` は `"proved"` または `"refuted"`。

`pyproject.toml` に `pythonpath = ["src"]` が既設。`from gl.letterless import ...` は通ります。
依存関係 `hypothesis>=6.100` も既設。

リポジトリには既存テスト 26 件があるので、全部走らせて、新規分含め `X passed` の内訳を
報告してください。

## 2. Formula 型への過剰な汎用性を削る

`letterless.py` の `_view`, `_normal_kind`, `_mapping_view`, `_field`, `_unary_child`,
`_binary_children`, `_nary_children`, `_as_sequence` などのヘルパは、Formula 型の **内部実装が
不明な場合に複数の典型形状に耐える** ためのものですよね。

リポジトリの `Formula` 型は **確定しています**：

```python
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
```

つまり：

- `f.type` は文字列、固定 8 種類
- 単項（`not`, `box`）は `f.arg`
- 二項（`imp`, `iff`）は `f.left`, `f.right`
- N 項（`and`, `or`）は `f.args` （tuple）

このスキーマに直接マッチさせて、汎用 view レイヤーを削ってください。具体的には：

- `_view(node)` は `(f.type, (children...))` を直接返す
- `_mapping_view`, `_field`, `_normal_kind`, `_unary_child`, `_binary_children`, `_nary_children`, `_as_sequence` は不要
- `aliases` 辞書も不要

`is_letterless`, `letterless_normal_form`, `nf_equiv` の **公開 API は変えない** でください。
内部の汎用層を削るだけです。

## 3. KAT テストの構造

KAT は dispatch の通り、独立 prover で 2 段階に確認してください：

```python
# tests/test_letterless_kats.py
from gl.formula import bot, Box, Not, Or, And, Imp, Iff, box_power
from gl.tableau import prove_gl
from gl.letterless import letterless_normal_form

def check(input_f, expected_nf):
    nf = letterless_normal_form(input_f)
    # 構文一致は要求しない。GL-同値かを独立 prover で確認
    assert prove_gl(Iff(input_f, nf)).status == "proved"
    assert prove_gl(Iff(nf, expected_nf)).status == "proved"
```

これ自体は前回満たしていたかもしれませんが、念のため。

## 4. engine と prover の分離テストを追加

`letterless.py` が `gl.tableau` / `gl.kripke_search` を import していないことを AST 解析で
自動チェックするテストを `tests/test_letterless_kats.py` の冒頭に追加してください：

```python
def test_letterless_does_not_import_provers():
    import ast, inspect
    import gl.letterless as letterless_module
    tree = ast.parse(inspect.getsource(letterless_module))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)
    assert "gl.tableau" not in imported_modules
    assert "gl.kripke_search" not in imported_modules
```

## 5. dispatch KAT 表の **訂正版** を RESULTS.md に明記

前回あなたが訂正してくれた件を、再度明示してほしいです。`RESULTS.md` に：

- 元の KAT 表で誤っていた行
- 正しい期待値
- 訂正の数学的根拠（短く、命題的同値 + Löb instance）

を 1 ブロックで書いてください。これは私（Claude Code）が指示書の `KAT 表`を訂正するときに
そのままコピペで使います。

## 提出形式

zip：

```
S2_letterless_normal_form_v2/
├── src/gl/letterless.py             # 汎用 view 層を削った版
├── tests/test_letterless_kats.py    # 独立 prover、AST 分離テスト追加
├── tests/test_letterless_random.py
└── RESULTS.md                        # 実走結果 X passed、KAT 訂正の根拠
```

期限：可能な限り早めにお願いします。
