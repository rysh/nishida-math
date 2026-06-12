# WP5 — headline 3 環境比較表

**日付**：2026-06-12
**スコープ**：指示書 §1「ONE SEED, THREE ENVIRONMENTS」の headline 表を 4 列に拡張、3 つの検証済み artifact から自動生成、CI で artifact 決定論性を検証
**結果**：136/136 通過（既存 128 + 新規 8）。MD・SVG・claims すべて再生成でバイト一致

## 設計判断（変更不可）

### 4 列構成

指示書 §1 の表は 3 列（Environment / Seed / Outcome）。本タスクではユーザ指定の 4 列に拡張：

| 列 | 役割 |
|---|---|
| Contradiction status | 種が生む矛盾を環境がどう扱うか |
| What follows from the seed | 矛盾から何が導かれるか |
| Formal witness | 主張を支える機械検証済み artifact（path + JSON キー） |
| Generativity | 3 環境を一本の軸で対比 — Classical = destroyed、LP = zero、GL = unbounded (linear n+2) |

指示書 §1 表は不変、本 WP5 表は **§1 の Outcome 列を 3 列に分解した拡張版** として位置づけ。指示書 L31「Every cell must be backed by a machine-checked artifact」と整合。

### `claims.json` を単一の source of truth とする

`build_claims.py` が 3 入力 artifact を読み、各セルの主張・artifact path・期待値を集約して `claims.json` に書き出す。**期待値が input artifact と一致しない場合は `AssertionError` を投げて manifest 出力を抑止**（hardcode 期待値の意義：指示書 §1 の主張そのものを running code で保証する仕組み）。

`build_table.py`（MD）と `build_figure.py`（SVG）は `claims.json` だけを読む。MD と SVG の主張がずれることが構造上不可能。

### Generativity 列の眼目

このプロジェクトの核：Classical と LP はどちらも「矛盾を最終状態として扱う」点で同類（一方は全面崩壊で何も区別できない、一方は不活性な隔離で何も生まない）。GL だけが矛盾を「次の段への移行を駆動する遷移的現象」として扱い、生成性を持つ。classical / tolerative の二項対立に対する第三の道（generative）の計算的実証。

SVG では Generativity 列だけ装飾を強める（背景色・bold・象徴的グリフ）：
- Classical = 赤系背景 + `⊥ ⊢ everything`
- LP = 黄系背景 + `0 (flatline)`
- GL = 青系背景 + `2 → 3 → 4 → … → n+2`

## 追加・変更したファイル

| ファイル | 役割 |
|---|---|
| `experiments/wp5/build_claims.py` | 新規。3 input artifact を検証しつつ `claims.json` を組み立てる |
| `experiments/wp5/build_table.py` | 新規。`claims.json` から `headline_table.md` を生成 |
| `experiments/wp5/build_figure.py` | 新規。`claims.json` から決定論的 SVG（hashsalt 固定・font をパス化・metadata なし） |
| `experiments/wp5/artifacts/claims.json` | 新規。WP5 の中心 artifact、MD と SVG の共通ソース |
| `experiments/wp5/artifacts/headline_table.md` | 新規。GitHub で render される headline 表 |
| `experiments/wp5/artifacts/headline_figure.svg` | 新規。論文用 figure |
| `tests/test_headline.py` | 新規。claims 構造、各セル ↔ artifact 整合性、MD 内容、SVG 決定論性 |
| `.github/workflows/test.yml` | 新規。pytest + 全 artifact 再生成 + `git diff --exit-code` |
| `docs/integration_notes/wp5_headline_table.md` | このノート |

## 各セルが artifact のどこを引いているか

### Classical 行（E-B1）

| セル | source artifact | キー / 値 |
|---|---|---|
| Contradiction status: explodes | hardcoded | — |
| What follows: everything (vacuous entailment) | hardcoded | — |
| Formal witness | `experiments/wp4/artifacts/e_b1_classical_explosion.json` | `satisfiable: false`、`vacuous_explosion: true`、`enumeration_size: 2` |
|  | `..._details.json` | `sample_vacuity_checks: [true, true, true, true, true]` |
| Generativity: destroyed | hardcoded | — |

build_claims が確認する不変式：`satisfiable is False`、`vacuous_explosion is True`、`sample_vacuity_checks` 5 件すべて True。

### LP 行（E-B2）

| セル | source artifact | キー / 値 |
|---|---|---|
| Contradiction status: tolerated | hardcoded | — |
| What follows: nothing new (inert) | hardcoded | — |
| Formal witness | `experiments/wp4/artifacts/e_b2_lp_quarantine.json` | `satisfiable: true`、`inert: true`、`mp_failure: {A:b, B:f}`、`ds_failure: {A:b, B:f}` |
|  | `..._details.json` | `liar_witness: {lambda:b}`、`liar_value_at_witness: "b"`、`inertness.violations: []` |
| Generativity: zero | hardcoded | — |

build_claims が確認する不変式：`satisfiable is True`、`inert is True`、MP/DS witness が `{A:b, B:f}`、liar の witness と value、inertness violations が空。

### GL 行（E-A2）

| セル | source artifact | キー / 値 |
|---|---|---|
| Contradiction status: resolved by ascent | hardcoded | — |
| What follows: a strictly higher consistency level | hardcoded | — |
| Formal witness | `experiments/wp3/artifacts/ladder_manifest.json` | `max_n: 8`、`exhaustive_max: 4`、9 stages すべて `monotone_status: "proved"`、`strict_status: "refuted"`、`countermodel_verified: true`、`witness_world_counts: [2..10]`、`minimality_exhaustively_checked` が n=0..4 で True、n=5..8 で False |
| Generativity: unbounded (linear n+2) | hardcoded（manifest の値と一致） | — |

build_claims が確認する不変式：`max_n == 8`、`exhaustive_max == 4`、`stages` 9 件、全 monotone proved、全 strict refuted、全 countermodel verified、witness counts が `[2..10]`、exhaustive flag が前 5 件 True / 後 4 件 False。

## 実走したテスト

```
$ uv run pytest tests/test_headline.py -v
collected 8 items
tests/test_headline.py ........                                          [100%]
============================== 8 passed in 0.77s ===============================

$ uv run pytest
136 passed in 18.88s
```

新規 8 件、既存 128 件、合計 **136 件通過**。

### 決定論性確認

3 つの WP5 artifact すべて 2 回生成してバイト一致：

```
$ for f in claims.json headline_table.md headline_figure.svg; do
    cp experiments/wp5/artifacts/$f /tmp/$f.r1
  done
$ uv run python experiments/wp5/build_claims.py > /dev/null
$ uv run python experiments/wp5/build_table.py > /dev/null
$ uv run python experiments/wp5/build_figure.py > /dev/null
$ for f in claims.json headline_table.md headline_figure.svg; do
    diff -q experiments/wp5/artifacts/$f /tmp/$f.r1
  done
(no output → all identical)
```

CI（`.github/workflows/test.yml`）でも同じ流れで `git diff --exit-code` が走る：
1. `uv sync` → `uv run pytest -q`
2. WP3、WP4、WP5 のすべての build スクリプトを順次実行
3. `git diff --exit-code` で artifact の変動なしを assert

ローカルで等価コマンドを実行し、`git status experiments/` が WP3、WP4 の committed artifact に対して clean なことを確認。

## WP5 Definition of Done 達成状況

| 要件 | 状態 |
|---|---|
| headline 表が 3 つの検証済み artifact から自動生成（MD + SVG） | ✅ `claims.json` を経由 |
| 各セルが claim manifest で artifact に紐づく | ✅ `formal_witness.artifact` + `keys` |
| CI セットアップ完了 | ✅ `.github/workflows/test.yml` |
| SVG 決定論的に再生成可能 | ✅ `test_figure_render_is_deterministic` で機械検証 |
| 全テスト実走で通過 | ✅ 136/136 |

**WP5 完了**。

## 残 WP の扱い

| WP | 状態 |
|---|---|
| WP1（GL prover）| ✅ T1 |
| WP2（fixed-point engine）| ✅ T2 |
| WP3（hierarchy + ladder）| ✅ T3 + S2 + ladder figure |
| WP4（LP / classical）| ✅ S1 |
| WP5（integration + headline + CI）| ✅ 本タスク |
| WP6（E-C2 Lean/Isabelle）| 🛑 後回し（指示書 §5 で stretch task として明記、必須ではない） |

指示書 §5「**Priority order:** WP1 → WP2 → WP3; WP4 parallel from day one; WP5 last; WP6 only if time remains.」に従い、WP6 は別判断。WP1〜WP5 がすべて Definition of Done を満たした現状、論文側執筆や Zenodo パッケージング、外部評価（S3 で Gemini Deep Research が報告した Lean 4 / Isabelle 識別子の実在検証）など、複数の進路がある。
