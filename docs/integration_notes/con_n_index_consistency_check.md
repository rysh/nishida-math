# Con_n インデックス整合性チェック

**日付**：2026-06-12
**スコープ**：KAT 表訂正（dispatch のみ）＋ Con_n インデックス整合性の機械チェック追加
**結果**：99/99 通過（既存 84 + 新規 15）

## 経緯と発見されたバグの所在

S2（letterless 正規形）の提出過程で、`Not(Box(Not(Box(bot))))` の期待 NF が
`Not(box_power(bot, 2))` ではなく `Not(box_power(bot, 1))` であるという指摘があった
（Löb instance `□(□⊥→⊥) → □⊥` による collapse）。本タスクではこの発見の出所と
影響範囲を機械的に切り分けた。

### 結論

- **指示書 `02 simspec kether nishida.md` 本体にはバグなし**。§2.2 KAT 表（行 55-61）、
  §2.3 Con_n 定義と正規形（行 68-72：`Con_n ≡ ¬□^{n+1}⊥`）、§1 ヘッドライン表、
  その他の Con_n 言及全行が一貫している。Phase 1 の Explore 調査で全数確認。
- **バグは `prompts/single/S2_dispatch.md` 130 行目の KAT 表 1 行**に局在。
  dispatch 作成時に Claude Code が `Not(Box(Not(Box(bot))))` を Con_1 と誤記したもの。
  S2 が v1 提出で発見し、v2 で訂正した。
- **実装側（T2 / T3 / S2）は最初から整合**。3 コンポーネント間で Con_n のインデックス
  解釈にずれはない。Phase 1 の Explore 調査で 7 箇所を確認。

## 指示書（`02 simspec kether nishida.md`）の整合性確認

§2.3 の正規形定理 `Con_n ≡ ¬□^{n+1}⊥` を基準とすると、以下が全文で一貫：

| 行 | 内容 | 整合 |
|---|---|---|
| 29 | 階層表記 `Con₀ ⊊ Con₁ ⊊ Con₂ ⊊ …` | ✓ |
| 57 | KAT: `¬□p` → `¬□⊥`（Gödel sentence = Con_0） | ✓ |
| 68 | 定義 `Con₀ := ¬□⊥; Con_{n+1} := ¬□¬Con_n` | ✓ |
| 70 | 正規形導出途中：`¬Con_n ≡ □^{n+1}⊥`、`Con_{n+1} ≡ ¬□^{n+2}⊥` | ✓ |
| 72 | 正規形結論 `Con_n ≡ ¬□^{n+1}⊥` | ✓ |
| 78 | (Monotone) `Con_{n+1} → Con_n` | ✓ |
| 79 | (Strict) `¬(Con_n → Con_{n+1})` ≡ `¬(□^{n+2}⊥ → □^{n+1}⊥)` | ✓ |
| 81 | n=0 KAT：線形 2-chain、一般 n は (n+2)-chain | ✓ |
| 121 | E-A2 実験：minimal countermodel = (n+2)-chain for n ≤ 4 | ✓ |

**指示書本体への訂正は不要**。

## 実装側 7 箇所の整合性確認

| 箇所 | 観察された値（Phase 1） | 評価 |
|---|---|---|
| `src/gl/formula.py::con` | `con(n) == Not(box_power(bot(), n + 1))` | ✓ |
| `src/gl/fixed_point.py` の Gödel KAT 経路 | `fixed_point(Not(Box(atom("p"))), "p")` → `Not(Box(bot()))` ≡ `con(0)` | ✓ |
| `src/gl/letterless.py` | `letterless_normal_form(Not(Box(bot())))` ≡ `Not(box_power(bot(), 1))` | ✓ |
| `experiments/wp3/build_countermodels.py` | `num_worlds = n + 2`、`formula = Imp(Con(n), Con(n + 1))` | ✓ |
| `tests/test_con_n_normal_form.py::Con` | 再帰：`Con(0) = ¬□⊥`、`Con(n+1) = ¬□¬Con(n)` | ✓ |
| `tests/test_letterless_kats.py` の対応 KAT | `Not(Box(bot()))` ↔ `Not(box_power(bot(), 1))` | ✓ |
| `prompts/single/S2_dispatch.md` 130 行（v1） | **誤**：`Not(Box(Not(Box(bot))))` → `Not(box_power(bot(), 2))` | **訂正** |

## 適用した訂正

### `prompts/single/S2_dispatch.md`

130 行目の右辺を訂正し、隣接行に Con_1 の真の例を追加：

```diff
- | `Not(Box(Not(Box(bot()))))` | `Not(box_power(bot(), 2))`（≡ Con_1） |
+ | `Not(Box(Not(Box(bot()))))` | `Not(box_power(bot(), 1))`（≡ Con_0、Con_1 ではない：Löb instance による collapse — 内側 `Not(Box(bot))` ≡ `Imp(Box(bot), bot)`、ゆえに `Box(Not(Box(bot)))` ≡ `Box(Imp(Box(bot), bot))` ≡ `Box(bot)`） |
+ | `Not(Box(Box(bot())))` | `Not(box_power(bot(), 2))`（≡ Con_1） |
```

`archive/` 配下の v1 dispatch 過去版は触らない（歴史的記録）。

### `tests/test_con_n_consistency.py`（新規）

T2 / T3 / S2 を横断する Con_n インデックス整合性を 4 観点で機械検証する pytest。
**reducer / engine は自己採点しない**：すべての同値判定は独立 prover
（`gl.tableau.prove_gl`）を呼ぶ。

| 観点 | 件数 | 内容 |
|---|---|---|
| 1 | 4（n=0..3） | `con(n)` が `Not(box_power(bot(), n+1))` と **構文一致** |
| 2 | 4（n=0..3） | `con(n)` と T3 再帰ヘルパ `Con(n)` が GL-同値 |
| 3 | 1 | Gödel 固定点 `fixed_point(¬□p, "p")` が `con(0)` と GL-同値 |
| 4 | 4（n=0..3） | `letterless_normal_form(con(n))` が `Not(box_power(bot(), n+1))` と GL-同値 |
| 5 (pin) | 1 | `letterless_normal_form(Not(Box(Not(Box(bot)))))` が `con(0)` と GL-同値（S2 訂正の核心） |
| 6 (pin) | 1 | `Not(Box(Box(bot())))` が `con(1)` と GL-同値（隣接する真の Con_1、上の対と峻別） |

T3 再帰ヘルパ `Con` は `tests/` が importable パッケージでないため、テスト内で
ミラー定義 `RecursiveCon` を置いた。drift が起きた場合は観点 2 が即時に検出する。

## 実走結果

```
$ uv run pytest tests/test_con_n_consistency.py -v
============================= test session starts ==============================
platform darwin -- Python 3.12.12, pytest-9.0.3, pluggy-1.6.0
configfile: pyproject.toml
plugins: hypothesis-6.155.2
collected 15 items

tests/test_con_n_consistency.py ...............                          [100%]

============================== 15 passed in 0.16s ==============================
```

```
$ uv run pytest
99 passed in 6.99s
```

新規 15 件、全 99 件通過。

## ladder figure に進む準備の判断

- 指示書本体は無傷で整合
- T2 / T3 / S2 / formula / letterless / build_countermodels の Con_n インデックス
  解釈は完全一致
- 新規追加した整合性テストにより、将来の回帰は CI で即時検出可能
- S2 訂正の核心（Löb instance collapse）も独立した pin として固定

**ladder figure 生成に進める**。次タスクで letterless growth 測定（指示書 §3 E-A2）と
ladder figure 描画に着手可能。
