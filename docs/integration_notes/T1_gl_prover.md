# T1 GL 証明器 — 統合判断ノート

**日付**：2026-06-10
**採用案**：ChatGPT
**統合方法**：A（そのまま採用、Grok/Gemini の取り込みなし）

## 3 案サマリ

| 観点 | Gemini | Grok | ChatGPT |
|---|---|---|---|
| Bot のスキーマ準拠 | ○ | ✗（`Atom("bot")` hack）| ◎ |
| 方法 A タブロー | △ 怪しい実装 | ✗ スタブ（kripke 委譲）| ◎ 本物の signed labelled tableau |
| 方法 B Kripke 探索 | △ 全 valuation 総当たり | ○ 最適化あり | ◎ topological normal form + filtration bound |
| 反例 verifier の独立性 | ○ | △（Formula 経由）| ◎ JSON 直接評価 |
| 2 法 cross-check の意味 | △ | ✗（同一関数）| ◎ |
| 指示書 L83 vs L70 の理解 | n=0..2 のみ | 本人がコメントで混乱 | 完全理解、両方を明示テスト |
| KAT n=0 最小反例 (2-鎖) | 未明示 | 暗黙 | 明示 assert |
| テスト | 未確認 | 未確認 | 15/15 確認済 |
| 出典 URL | なし | なし | あり |

## 判定理由

ChatGPT 案が唯一、指示書 §6 の Formula JSON スキーマを完全準拠（`{"type":"bot"}` を `Formula("bot")` で正しく実装）し、かつ Method A タブローと Method B Kripke 探索が **真に独立した 2 実装** になっており、指示書 L166 の cross-check 要件を実質的に満たしている。

Grok 案の Method A は kripke_search に丸投げのスタブで、本人も §0 自己申告で「Full GL tableau ... is notoriously easy to get wrong」と述べて代替実装にしている。Gemini 案の Method A は本物の実装に見えるが、ループ検出が S4 的（successor に T(□A) を残す）で GL の核心を外している可能性がある。

特に決定的だったのは、ChatGPT が **指示書 L83**（`GL ⊢ ¬□⊥ → ¬□¬□⊥`、第二不完全性の形）と **指示書 L70**（`GL ⊬ Con_n → Con_{n+1}`、特に n=0 で `¬□⊥ → ¬□□⊥`）を **別の式として明示的にテストし両方通している** こと。Grok のテストは両者を混同して困惑コメントを残しており、Gemini は片方しか触れていない。

両式の違い：
- `¬□⊥ → ¬□¬□⊥`：右辺の □ の中に **¬** が入っている（定理）
- `¬□⊥ → ¬□□⊥`：右辺は連続した □（非定理）

## Grok から取り入れなかったが価値のある要素（将来の選択肢）

- `lru_cache` でフレーム生成キャッシュ
- `pretty` printer の Unicode 記号
- `frozen=True` dataclass

これらは ChatGPT 案にも `@dataclass(frozen=True, slots=True)` や Unicode pretty が既に入っており、性能改善は当面不要なので取り込み見送り。

## Gemini Deep Research (S3) の扱い

S3（Lean 4 / Isabelle 不完全性 formalization 調査）の結果は `incoming/S3_lean_isabelle_survey/gemini.md` に保存済み。**WP6 着手は後回し**との方針なので、URL・識別子の実在検証はペンディング。

## 未検証で気になる点（次にやる候補）

1. Method B の `world_bound = #distinct box subformulas + 1` で Con_n の n=5..8 までの strict refutation が到達するか
2. Method A のループ検出が深いネスト式で誤検出しないか
3. random battery の 1000 件が本当に走っているか（hypothesis のドット 1 個の意味）

## 採用したファイル

- `src/gl/formula.py`
- `src/gl/tableau.py`（Method A）
- `src/gl/kripke_search.py`（Method B）
- `src/gl/countermodel_verifier.py`
- `tests/test_gl_kats.py`
- `tests/test_gl_random.py`
- `pyproject.toml`
