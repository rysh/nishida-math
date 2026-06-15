# WP6 着手判断のための調査結果（S3）

出典：`incoming/S3_lean_isabelle_survey/gemini.md`（Gemini Deep Research, 2026-06-10）
Claude Code による一次ソース照合：2026-06-15（本ファイル末尾「検証ログ」参照）

## 結論（WP6 の形が変わる）

E-C2（F → F+Con(F) の一段階を機械検証）は **ゼロから formalize する作業ではない**。
2026 年 6 月時点で、Lean 4 の `FormalizedFormalLogic/Foundation`（sorry-free）に
G2 と「F ⪱ F + Con(F)」が **既にインスタンスとして存在**する。よって E-C2 は
**「既存ライブラリを具体的な基底理論で呼び出し、ステージ 1 の真の強化を 1 インスタンス機械検証する」**
タスクに縮小される。指示書 §3 の「Do NOT re-formalize incompleteness from scratch」が
文字通り達成可能。

## 一次ソースで確認済みの事実（Claude Code 照合）

`Foundation/FirstOrder/Incompleteness/Second.lean`（master, 確認日 2026-06-15）に以下が存在：

```lean
/-- Gödel's second incompleteness theorem -/
theorem consistent_unprovable [Consistent T] : T ⊬ ↑T.consistent :=
  ProvabilityAbstraction.con_unprovable (𝔅 := T.standardProvability)

instance [Consistent T] : T ⪱ T + T.Con :=
  StrictlyWeakerThan.of_unprovable_provable (φ := ↑T.consistent)
    (consistent_unprovable T)
    (Entailment.by_axm _ (by simp [Theory.add_def]))

theorem inconsistent_unprovable [ArithmeticTheory.SoundOnHierarchy T 𝚺 1] :
  T ⊬ ∼↑T.consistent := ...

theorem inconsistent_independent [ArithmeticTheory.SoundOnHierarchy T 𝚺 1] :
  Independent T ↑T.consistent := ...
```

- `T ⪱ T + T.Con`（`⪱` = `StrictlyWeakerThan`）が **まさに「F は F+Con(F) より真に弱い」**＝
  ステージ 1 の真の強化。これがそのまま E-C2 の主成果になる。
- 任意の `[Consistent T]`（`IΣ₁` 以上）で成立する一般形。基底 `T` を具体化すれば 1 インスタンス。
- arXiv:2604.07406 が同ライブラリを「sorry-free, machine-checked proofs of both Gödel
  incompleteness theorems」と明記（第三者利用の傍証）。

## 推奨選択肢

**Lean 4 + FormalizedFormalLogic/Foundation を第一候補**とする。理由：
1. `⪱`（StrictlyWeakerThan）で「真の強化」が**型レベルの一級概念**として既にある。
   E-C2 が要求する「stage 1 で新定理が出る」が、まさにこのインスタンス。
2. Solovay 算術的完全性も同リポジトリにあり、本体（GL 階層）との接続を語れる。
3. sorry-free。Zenodo 配布時の信頼性。

Isabelle/HOL（AFP: Paulson の HF ベース → Popescu–Traytel の Locale 抽象化 →
Bailitis の Löb 統合）も完成度は同等。ただし本プロジェクトの GL 中心線（Solovay）
との地続き感は Lean 側が上。**どちらでも E-C2 は達成可能**。

## 既知の落とし穴（実装前に読む）

- **相対無矛盾性の連鎖**：Lean 自身の無矛盾性は ZFC（+到達不能基数）に相対化されている。
  「PA ⊬ Con(PA) を、自身の Con を証明できない ZFC 基盤の Lean が俯瞰検証する」という
  入れ子構造。RESULTS には「機械検証＝絶対的無矛盾性の保証」と書かない（§7 と整合）。
- **基底理論の取り違え**：`IΣ₁` 以上であることが `[Consistent T]` 系インスタンスの前提。
  具体化する `T` がこの条件を満たすか型レベルで確認。
- **バージョン固定**：Mathlib / Foundation は活発に動く。lakefile で commit ピン留め必須
  （再現性。Makefile `verify` の決定性要件と同じ思想）。
- **ライセンス/アトリビューション**：配布前に LICENSE 確認。引用語法は §7（"provides
  formal support for / consistent with"）。Saito（Palalansoukî）+ Noguchi（SnO2WMaN）への
  クレジット。

## E-C2 最短経路（Lean 採用時）

1. Foundation を依存に追加（lakefile、commit ピン留め）、`lake build` 成功確認。
2. `Second.lean` の `consistent_unprovable` と `instance : T ⪱ T + T.Con` を import。
3. 具体基底 `T`（`IΣ₁` 以上の既提供理論）を 1 つ選び、`T ⪱ T + T.Con` を **その T で**
   インスタンス化 → ステージ 1 の真の強化を 1 つ機械検証（これが E-C2 の deliverable）。
4. ステージ 1→2 まで触れるなら `T + T.Con ⪱ (T + T.Con) + (T + T.Con).Con` を試みる
   （任意。GL 側の Con_n 階層との対応注記に使える）。
5. `RESULTS.md` に「これは既知結果（Saito–Noguchi）の**インスタンス化による形式的裏付け**で
   あり、新規数学ではない」と明記。本体の GL letterless 階層（E-A2）と**同じ現象の算術側の影**
   である、と構造的にのみ接続（因果語法・予見語法は使わない）。

## 参考 URL（一次）

- https://github.com/FormalizedFormalLogic/Foundation
- https://github.com/FormalizedFormalLogic/Foundation/blob/master/Foundation/FirstOrder/Incompleteness/Second.lean
- https://formalizedformallogic.github.io/Foundation/
- arXiv:2604.07406（第三者による sorry-free 利用の傍証）
- Isabelle/AFP: Paulson "Gödel's Incompleteness Theorems"; Popescu–Traytel "From Abstract to
  Concrete Gödel's Incompleteness Theorems"（AFP エントリ名は配布前に再確認）

## 検証ログ（Claude Code, 2026-06-15）

- `Second.lean` の主要宣言（`consistent_unprovable`, `instance : T ⪱ T + T.Con`,
  `inconsistent_unprovable`, `inconsistent_independent`）を GitHub 一次ソースで確認。
  Gemini 報告のコードと一致。
- リポジトリ存在・メンテナ（Saito/Noguchi）・「Logic Zoo」「Provability Logic」「Solovay
  完全性」収録を公式 README / GitHub Pages で確認。
- 未確認（配布前に詰める）：AFP の正確なエントリ名と対応 Isabelle バージョン、Foundation の
  ピン留め対象 commit、選定する具体基底理論 T の名前空間。
