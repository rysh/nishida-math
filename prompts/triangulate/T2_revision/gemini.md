# T2 修正依頼（Gemini 宛、同じスレッドで続けて貼る）

前回の T2 提出（k-decomposition + outermost p-box 抽出）を Claude Code がレビューしました。
**アルゴリズムの方向性は正しいです**。ただし以下を修正してください。

## 1. 確実なバグ：`substitute_formula` の `iff` 右辺

`src/gl/fixed_point.py` の `substitute_formula` 関数、`iff` のケース：

```python
elif formula.type == "iff":
    return Iff(substitute_formula(formula.left, target, replacement), substitute(formula.right, target, replacement))
                                                                       ^^^^^^^^^^
                                                                       これは bug
```

右側で `substitute_formula` を呼ぶべきところを `substitute` を呼んでいます。`substitute` は
**atom 名で置換**する関数で、ここでは **部分式単位で置換**しなければなりません。
これにより `iff` 内で右辺の部分式置換が完全にスキップされます。

**修正**：右側も `substitute_formula(formula.right, target, replacement)` に直してください。

## 2. 実走確認（必須）

前回「実装まで」で実走確認なしでした。今回は実走させてください。

リポジトリトップで：

```bash
uv run pytest -q
```

リポジトリの src tree：

```
src/gl/__init__.py             # 空
src/gl/formula.py              # Formula, ProofResult, bot(), atom(), Not(), And(), Or(),
                               # Imp(), Iff(), Box(), box_power(), con(), atoms(), subformulas(),
                               # modal_depth(), pretty() を export
src/gl/tableau.py              # prove_gl(formula: Formula) -> ProofResult
src/gl/kripke_search.py        # prove_gl(formula: Formula) -> ProofResult
src/gl/countermodel_verifier.py # verify_countermodel(formula, model_json) -> bool
```

`ProofResult.status` は `"proved"` または `"refuted"`（`"unproved"` ではありません）。
`pyproject.toml` に `pythonpath = ["src"]` 既設なので、`from gl.fixed_point import ...` は通ります。

`X passed` の内訳を `RESULTS.md` に報告してください。リポジトリには既存テスト 26 件があるので、
全部走らせて壊れていないことも確認してください。

## 3. 第 2 アルゴリズム（alt）の独立性

前回 alt は提出されていますか？ もし提出している場合は、主実装との独立性について
報告してください。同じ k-decomposition 原理なら、せめて：

- 主実装：再帰的（trees of substitution）
- alt：iterative（loop で placeholder を順に解消）

くらいの差を入れて、uniqueness テストで「実装の独立性」が形だけでも担保されるようにしてください。

## 4. random battery の規模

dispatch では「≥ 200 件」を要求しました。これを満たし、実走して通った件数を報告してください。

## 5. KAT の独立検証構造

dispatch で示した KAT の検証パターン：

```python
def assert_fixed_point(A, p, expected_H):
    H = fixed_point(A, p)
    # 独立 prover で 2 つを検証
    equiv_to_expected = Iff(H, expected_H)
    assert prove_gl(equiv_to_expected).status == "proved"
    fp_equation = Iff(H, substitute(A, p, H))
    assert prove_gl(fp_equation).status == "proved"
```

このパターンを `tests/test_fixed_point_kats.py` に使っていますか？ もし「自分の構築したものと
構文一致するか」を見るパターンで書いていたら、それは engine の正しさを engine 自身で
確認したことになるので不可です。**独立 prover に `Iff(...)` を渡して `proved` か聞く** 形に
してください。

## 6. AST レベルでの engine/prover 分離テスト

ChatGPT 案には以下のようなテストが入っていて、これは堅牢です：

```python
def test_engine_modules_do_not_import_provers():
    import ast, inspect
    import gl.fixed_point as fixed_point_module
    import gl.fixed_point_alt as fixed_point_alt_module
    for module in (fixed_point_module, fixed_point_alt_module):
        tree = ast.parse(inspect.getsource(module))
        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)
        assert "gl.tableau" not in imported_modules
        assert "gl.kripke_search" not in imported_modules
```

同様のテストを `tests/test_fixed_point_kats.py` の冒頭に追加してください。

## 提出形式

zip：

```
T2_fixed_point_gemini_v2/
├── src/gl/fixed_point.py         # substitute_formula bug 修正済
├── src/gl/fixed_point_alt.py     # alt（あれば、独立性レベルを RESULTS.md に書く）
├── src/gl/modalized.py
├── tests/test_fixed_point_kats.py
├── tests/test_fixed_point_random.py
├── tests/test_fixed_point_uniqueness.py
└── RESULTS.md                     # 実走結果 X passed、bug 修正の確認、独立性レベルの報告
```

期限：可能な限り早めにお願いします。
