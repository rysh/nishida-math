# S7 送信用合体プロンプト（WP6 E-C2 Lean インスタンス化 / 単独 LLM）

> このファイルは、S7（WP6 E-C2 Lean4 ステージ1強化の機械検証）を
> **ChatGPT GPT-5 または Gemini 2.5 Pro** に投げるための合体プロンプトです。
> 下のセクション（区切り線で囲まれた部分）を **そのままコピペ** して新規スレッドで送ってください。
>
> 戻ってきた成果物は `incoming/S7_wp6_lean_instantiation/<llm>.md`
> （`<llm>` は `chatgpt` または `gemini`）に置いてください。
> 添付の `.lean` / `lakefile` は同ディレクトリに別ファイルで置いても OK。

---

> あなたは「ケーテル西田 / Generative Contradiction」プロジェクトの計算的展示を作るための
> **補助エージェント**です。あなたの出力はそのまま採用されません。Claude Code が読み、
> 必要に応じて検証パイプラインに通します。あなたの責務は「最善を尽くす」だけでなく、
> **どこに不確かさがあるかを正直に申告する**ことを含みます。
>
> ## プロジェクトの骨子
>
> Nishida Kitarō の絶対矛盾的自己同一と Gödel 不完全性が同じ **productive self-reference**
> 構造を記述している、という哲学的主張の **illustration**（証明ではない）を、
> 機械検証された artifacts として作る。
>
> 同じ自己言及種を 3 環境に植える：
>
> 1. **古典命題論理** — λ ↔ ¬λ は充足不可能 → 爆発
> 2. **LP（Priest, 3 値）** — v(λ)=b で充足。λ-free 言語では何も新しく従わない（inert）
> 3. **GL（Gödel–Löb 証明可能性論理）** — Gödel 型固定点 H ↔ ¬□H が ¬□⊥ ≡ Con に解け、
>    Con₀ ⊊ Con₁ ⊊ Con₂ ⊊ … の厳密無限階層を launch（generation）
>
> WP6 は本体（WP1–5）完成後の **任意・装甲増し** 拡張。E-C2 は GL 階層（E-A2）の
> **算術側の影** を、既存ライブラリで 1 インスタンス機械検証する位置づけ。
>
> ## 不変式（破ったら不採用）
>
> - 出力する Lean コード・主張・文章は、Claude Code 側で `lake build` 実機確認＋
>   型チェック検証されて初めて採用される。
> - **禁止表現**（指示書 §7）：
>   1. シミュレーション／機械検証が「哲学的テーゼを **証明する**」
>   2. 「西田が Gödel を **予見した**」（歴史的主張として）
>   3. 数学的内容に対する **新規性主張**（Saito–Noguchi の `Foundation` 既知結果のインスタンス化である）
>   4. 「機械検証＝絶対的無矛盾性の保証」（Lean 自身の無矛盾性は ZFC に相対化されている）
>   5. 因果消去主義的一般化
> - **引用語法**："consistent with / converges with / provides formal support for" を既定。
>   "building on / following" は西田と本論文著者にのみ用いる。
> - **認識論的位置づけ**：「既存ライブラリのインスタンス化による形式的裏付け」を明示。
>
> ## このタスク特有の注意
>
> - **再 formalize 禁止**：不完全性をゼロから書かない。`FormalizedFormalLogic/Foundation`
>   の `consistent_unprovable` / `instance [Consistent T] : T ⪱ T + T.Con` を **そのまま呼ぶ**。
> - **build 捏造禁止**：通っていないなら「通っていない」と明記。通った風を装うのは最悪。
> - **commit ピン留め必須**：Mathlib / Foundation は活発に動くので、再現性のため必ず固定する。
> - **基底理論の前提**：`[Consistent T]` 系インスタンスは `IΣ₁` 以上を要求する。
>   選ぶ `T` がこの条件を型レベルで満たすことを確認する。
> - **API 名は調査済み表記に合わせる**：`StrictlyWeakerThan`, `T.Con`, `consistent_unprovable`,
>   `Theory.add_def` 等。変えるなら理由を書く。
> - **アトリビューション**：Saito = Palalansoukî, Noguchi = SnO2WMaN。

---

## タスク

### 文脈（指示書 §3 E-C2、WP6 表）

> Arithmetic-level single iteration F → F+Con(F) using an **existing** incompleteness
> formalization. **Do NOT re-formalize incompleteness from scratch.**
> Deliverable: one machine-checked instance of "new theorem at stage 1."
> WP6 DoD: One machine-checked instance; clearly marked optional.

S3 調査（Gemini Deep Research, 2026-06-10、Claude Code が一次ソース照合済み）により、
2026-06 時点で Lean 4 `FormalizedFormalLogic/Foundation`（sorry-free）に既に以下が存在する：

```lean
-- Foundation/FirstOrder/Incompleteness/Second.lean
theorem consistent_unprovable [Consistent T] : T ⊬ ↑T.consistent :=
  ProvabilityAbstraction.con_unprovable (𝔅 := T.standardProvability)

instance [Consistent T] : T ⪱ T + T.Con :=
  StrictlyWeakerThan.of_unprovable_provable (φ := ↑T.consistent)
    (consistent_unprovable T)
    (Entailment.by_axm _ (by simp [Theory.add_def]))
```

`⪱` = `StrictlyWeakerThan`。`T ⪱ T + T.Con` が
**「F は F+Con(F) より真に弱い」＝ステージ1の真の強化** そのもの。
本タスクの成果はこれを **具体的な基底理論で 1 インスタンス機械検証**すること。

参考 URL（一次）：
- https://github.com/FormalizedFormalLogic/Foundation
- https://github.com/FormalizedFormalLogic/Foundation/blob/master/Foundation/FirstOrder/Incompleteness/Second.lean
- https://formalizedformallogic.github.io/Foundation/

### 1. 環境（再現可能性が最重要）

- `lakefile`（`lakefile.lean` または `lakefile.toml`）で `Foundation` を依存に追加。
  **commit を必ずピン留め**（タグ or revision 固定）。
- `lake build` が通る最小構成。使用した Lean toolchain（`lean-toolchain` の中身）、
  Foundation の commit hash、Mathlib バージョンを明記。
- ネットワーク／ビルド時間の制約があれば正直に申告（「ローカルで build 未確認」等）。

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

- これは Saito–Noguchi らの **既知結果のインスタンス化による形式的裏付け** であり新規数学ではない。
- 本体 GL の Con_n 階層（E-A2）と **同一現象の二つの現れ** として **構造的にのみ** 接続。
- **禁止**：「証明する（哲学的テーゼを）」「予見」「新発見」「機械検証＝絶対的無矛盾性」。
- Lean 自身の無矛盾性が ZFC に相対化されている点に 1 行触れると誠実（任意）。

### 4. 落とし穴の自己点検

- 基底 `T` が `[Consistent T]` 系インスタンスの前提（`IΣ₁` 以上）を満たすか型レベルで確認したか。
- commit ピン留めをしたか。
- ライセンス／アトリビューション（Saito=Palalansoukî, Noguchi=SnO2WMaN）。

---

## §0 自己申告（必須・成果物の先頭に置く）

- 確信度：High / Medium / Low（このタスク全体について）
- 不安な箇所（具体的に、最低 3 つ）
- 参照した文献・URL
- ハルシネーション可能性が高い記述（自分で気付いたもの）

たとえば：
- 選んだ基底理論 `T` の Foundation 内の正確な名前空間
- `[Consistent T]` の前提が選んだ `T` で型クラス推論される根拠
- lakefile の依存記述（特に Mathlib バージョン整合）

## 出力形式

成果物全体を以下の構造で：

````
## §0 自己申告

## 結論（3 行：何を 1 インスタンス検証したか／build 状況／未確認事項）

## 環境
- lean-toolchain:
- Foundation commit:
- Mathlib version:
- lakefile（全文、fenced code block）

## E-C2 本体 .lean（全文、コメントつき、fenced code block）

## build ログ（通ったなら要約、通らない／未確認なら正直に）

## RESULTS 文言案（§7 準拠、3〜5 行）

## 落とし穴自己点検（チェックリストへの回答）

## 不明・未達（正直に列挙）
````

## 重要（再掲）

- **build が通っていない場合は「通っていない」と書く。** 通った風の捏造は最悪。
- API 名（`StrictlyWeakerThan`, `T.Con`, `consistent_unprovable`, `Theory.add_def` 等）は
  Foundation の確認済み表記に合わせる。変えたなら理由を書く。
- 指示書 §7 禁止表現・引用語法を全文でチェック。
- 自信のない箇所は §0 で「不安」と申告（その箇所は実際に誤っている率が高い）。
