# S3: WP6 (E-C2) Lean4 / Isabelle 不完全性 formalization 調査

> 🎯 これは **単独 LLM タスク**（指定：Gemini 2.5 Pro **Deep Research** モード）。
> 既存 formalization の現存確認は Web 探索の問題、Gemini Deep Research の独壇場。
>
> **前置き**：`_shared/preamble.md` を冒頭に貼る。

---

## 調査依頼

指示書 §3 E-C2：

> Arithmetic-level single iteration F → F+Con(F) using an **existing** incompleteness
> formalization (Isabelle/HOL: Paulson 2015; Lean 4 community libraries —
> agents verify current availability).
> **Do NOT re-formalize incompleteness from scratch.**
> Deliverable: one machine-checked instance of "new theorem at stage 1."

**2026-06-10 時点**で何が利用可能かを Deep Research で明らかにする。

## 調査項目

### A. Lean 4 / Mathlib

1. Mathlib に Gödel 第一・第二不完全性定理がマージ済みか
   - ファイルパス・名前空間・主定理名
   - 該当 PR / commit / Mathlib バージョン
2. マージ前なら：未マージ PR、フォーク、個別リポジトリ、メンテナの活動状況
3. `Con(PA)` または `Con(F)` の Σ₁ 文としての表現の有無
4. 「F + Con(F) の Con(F + Con(F))」を直接記述できる API の有無

### B. Isabelle/HOL

1. Paulson 2015 不完全性 formalization の現状
   - AFP エントリ名・URL
   - 直近更新日、対応 Isabelle バージョン
2. Σ₁ 完全性、対角化補題、第二不完全性の定理名
3. F + Con(F) 拡張をユーザーが宣言する作法

### C. その他

1. Coq / Rocq、Agda、Metamath の類似 formalization
2. **「F → F+Con(F) 単一反復」を最小実装コストで示せる選択肢**
   - 学習コスト、ライブラリ成熟度、ドキュメント、コミュニティ活発度の 4 軸比較
3. ライセンスとアトリビューション（Zenodo 配布可否）

### D. 落とし穴

- Con(F) の sentence-level encoding を Σ₁ で書く標準的やり方
- 拡張系 F + Con(F) を新 theory として宣言する作法
- 拡張系での Con(F + Con(F)) を外側で証明する最短経路

## 出力形式

```
## 結論（3 行）

## 推奨選択肢（Lean4 vs Isabelle vs その他、根拠つき）

## A. Lean 4 / Mathlib 詳細
- マージ状況 / 主要 API / 出典 URL

## B. Isabelle/HOL 詳細
- AFP エントリ / 主要定理 / 出典 URL

## C. 代替候補

## D. 既知の落とし穴

## E. E-C2 実装の最短経路（推奨選択肢でのステップ概要）

## 参考文献・URL リスト
```

## 重要

- **すべての主張に URL ソース**
- **2026-06-10 時点** の最新確認を明示
- 不明は「不明」と書く
- ライブラリ名・定理名は **正確に**
- 指示書 §7 の禁止表現と引用語法を守る

Claude Code は結果を `docs/wp6_survey.md` に保存し、WP6 着手判断に使う。
