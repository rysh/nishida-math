# S7: WP6 (E-C2) Lean4 ステージ1強化の機械検証

> 🎯 これは **単独 LLM タスク**（推奨：ChatGPT GPT-5 または Gemini 2.5 Pro）。
> 既存ライブラリ `FormalizedFormalLogic/Foundation` の **インスタンス化**であり、
> 不完全性の再 formalize ではない。環境構築の正確さが成否を分ける。
>
> **前置き**：`_shared/preamble.md` を冒頭に貼る。
> **必読**：`docs/wp6_survey.md`（S3 調査の照合済み結果）。本タスクはそれを前提に書かれている。

---

## 文脈（指示書 §3 E-C2、WP6 表）

> Arithmetic-level single iteration F → F+Con(F) using an **existing** incompleteness
> formalization. **Do NOT re-formalize incompleteness from scratch.**
> Deliverable: one machine-checked instance of "new theorem at stage 1."
> WP6 DoD: One machine-checked instance; clearly marked optional.

`docs/wp6_survey.md` により、2026-06 時点で Lean 4 `FormalizedFormalLogic/Foundation`
（sorry-free）に既に以下が存在することが**一次ソースで確認済み**：

```lean
theorem consistent_unprovable [Consistent T] : T ⊬ ↑T.consistent
instance [Consistent T] : T ⪱ T + T.Con     -- ⪱ = StrictlyWeakerThan
```

`T ⪱ T + T.Con` が **「F は F+Con(F) より真に弱い」＝ステージ1の真の強化** そのもの。
本タスクの成果はこれを **具体的な基底理論で 1 インスタンス機械検証**すること。

## 依頼

### 1. 環境（再現可能性が最重要）

- `lakefile`（lakefile.lean または lakefile.toml）で `Foundation` を依存に追加。
  **commit を必ずピン留め**（タグ or revision 固定）。理由：Mathlib/Foundation は活発に動く。
- `lake build` が通る最小構成。使用した Lean toolchain（`lean-toolchain` の中身）、
  Foundation の commit hash、Mathlib バージョンを明記。
- ネットワーク/ビルド時間の制約があれば正直に申告（「ローカルで build 未確認」等）。

### 2. インスタンス化（E-C2 本体）

- `IΣ₁` 以上の具体基底理論 `T` を 1 つ選ぶ（Foundation が提供するものから。名前空間を正確に）。
- その `T` について `T ⪱ T + T.Con` を呼び出し、ステージ1の真の強化を機械検証する
  最小の `.lean` ファイルを書く。
- 成果の意味を 1 行コメントで：`Con(T)` は `T` で証明不能だが `T + T.Con` で自明に証明可能、
  ゆえに真に強い——これが E-A2（GL 側 letterless 階層）の算術側の影。
- **任意**：ステージ 1→2（`T + T.Con ⪱ (T + T.Con) + _.Con`）も触れられれば触れる。
  できなければ「未達」と明記。無理に通った風を装わない。

### 3. RESULTS への文言案（§7 厳守）

3〜5 行で：
- これは Saito–Noguchi らの**既知結果のインスタンス化による形式的裏付け**であり新規数学ではない。
- 本体 GL の Con_n 階層（E-A2）と**同一現象の二つの現れ**として**構造的にのみ**接続。
- **禁止**：「証明する（哲学的テーゼを）」「予見」「新発見」「機械検証＝絶対的無矛盾性」。
- Lean 自身の無矛盾性が ZFC に相対化されている点に 1 行触れると誠実（任意）。

### 4. 落とし穴の自己点検（`docs/wp6_survey.md`「既知の落とし穴」と照合）

- 基底 `T` が `[Consistent T]` 系インスタンスの前提（`IΣ₁` 以上）を満たすか型レベルで確認したか。
- commit ピン留めをしたか。
- ライセンス/アトリビューション（Saito=Palalansoukî, Noguchi=SnO2WMaN）。

## 出力形式

````
## 結論（3 行：何を 1 インスタンス検証したか／build 状況／未確認事項）

## 環境
- lean-toolchain:
- Foundation commit:
- Mathlib version:
- lakefile（全文）

## E-C2 本体 .lean（全文、コメントつき）

## build ログ（通ったなら要約、通らない/未確認なら正直に）

## RESULTS 文言案（§7 準拠）

## 落とし穴自己点検（チェックリストへの回答）

## 不明・未達（正直に列挙）
````

## 重要

- **build が通っていない場合は「通っていない」と書く。** 通った風の捏造は最悪。
- ライブラリの API 名（`StrictlyWeakerThan`, `T.Con`, `consistent_unprovable`,
  `Theory.add_def` 等）は `docs/wp6_survey.md` の確認済み表記に合わせ、変えたなら理由を書く。
- 指示書 §7 禁止表現・引用語法を全文でチェック。
- 自信のない箇所は §0 で「不安」と申告（その箇所は実際に誤っている率が高い）。

Claude Code は受領後：(1) Foundation を当該 commit で取得し `lake build` 実機確認、
(2) インスタンスが本当に型チェックを通るか検証、(3) §7 スキャン、
(4) 採用なら `experiments/wp6/` に配置し `RESULTS.md`・headline 外の補遺に反映、
`archive/S7_wp6_lean_instantiation/` へ退避。
