# S7（WP6 E-C2 Lean インスタンス化）受領後の検証手順

**作成日**：2026-06-15
**ステータス**：dispatch 前（LLM 出力未受領）
**スコープ**：S7 dispatch を出してから、LLM 出力を受領した Claude Code がやるべき作業の事前文書化

## 前提

- S7 は **単独 LLM タスク**（推奨：ChatGPT GPT-5 または Gemini 2.5 Pro）。
- ディスパッチプロンプトは [`prompts/single/S7_wp6_lean_instantiation.md`](../../prompts/single/S7_wp6_lean_instantiation.md)。
- LLM が必読とする調査結果は [`docs/wp6_survey.md`](../wp6_survey.md)。Claude Code が GitHub 一次ソースで照合済（確認日 2026-06-15）。
- E-C2 のゴール：`FormalizedFormalLogic/Foundation` の既存定理 `theorem consistent_unprovable` と `instance [Consistent T] : T ⪱ T + T.Con` を **具体的な基底理論 `T`（`IΣ₁` 以上）で 1 インスタンス機械検証**。新規 formalize はしない。

## 受領時に LLM 出力に含まれるはずのもの

[`prompts/single/S7_wp6_lean_instantiation.md`](../../prompts/single/S7_wp6_lean_instantiation.md) の出力形式セクション参照。期待される項目：

1. 結論 3 行（何を 1 インスタンス検証したか／build 状況／未確認事項）
2. 環境：`lean-toolchain` 中身、`Foundation` の commit hash、`Mathlib` バージョン、`lakefile` 全文
3. E-C2 本体 `.lean` 全文（コメントつき）
4. `lake build` ログ（通った/通らない/未確認）
5. RESULTS 文言案（§7 準拠、3〜5 行）
6. 落とし穴自己点検（チェックリスト）
7. 不明・未達（正直な列挙）

## Claude Code がやる検証手順

### Step 1: 出力の最低限スクリーニング（数分）

- [ ] § 0 自己申告で「不安」と書かれた箇所がないか → あれば実際に間違っている可能性高、注視。
- [ ] `lake build` が「通っていない」「未確認」と書かれているか → 通った風の捏造を疑う癖。LLM が「通った」と書いていても次の Step で実機確認する。
- [ ] 指示書 §7 forbidden phrases を `RESULTS 文言案` で grep。下記スキャンスクリプト参照。
- [ ] API 名（`StrictlyWeakerThan`, `T.Con`, `consistent_unprovable`, `Theory.add_def` 等）が `docs/wp6_survey.md` の確認済み表記と一致するか。違うなら LLM の理由説明があるか。

```bash
# §7 forbidden phrases スキャン例
for phrase in "proves the philosophical thesis" "Nishida anticipated" "we prove" "novel theorem" \
              "our novel" "the constraint generates" "causes the ascent" \
              "machine-checked absolute consistency" "guarantees absolute consistency"; do
  grep -nFi "$phrase" incoming/S7_wp6_lean_instantiation/*.md || true
done
```

### Step 2: Lean toolchain のインストール（受領時に初めて入れる）

事前にインストールしていない理由：LLM 指定の `lean-toolchain` バージョンに合わせたい。

```bash
# elan を ~/.elan/ 隔離インストール（非破壊）
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y --default-toolchain none
source "$HOME/.elan/env"
elan --version  # 確認
```

その後、LLM が指定した `lean-toolchain`（例：`leanprover/lean4:v4.10.0`）で具体的に：

```bash
mkdir -p /tmp/s7-build && cd /tmp/s7-build
cp incoming/S7_wp6_lean_instantiation/<llm>/lean-toolchain .
elan toolchain install $(cat lean-toolchain)
lean --version
lake --version
```

### Step 3: `Foundation` を pin commit で取得し `lake build`

LLM の lakefile を貼り、commit を指定通り pin した状態で：

```bash
cp incoming/S7_wp6_lean_instantiation/<llm>/lakefile.* /tmp/s7-build/
cp incoming/S7_wp6_lean_instantiation/<llm>/*.lean /tmp/s7-build/
cd /tmp/s7-build && lake build 2>&1 | tee build.log
```

通らなければ：
- LLM の指定 commit が削除されていないか確認（`Foundation` の master が動く）。
- Mathlib との互換 ver 問題なら lakefile の Mathlib pin を確認。
- 通らない理由が明確になるまで「採用」と書かない。

### Step 4: インスタンスの型チェック確認

`lake build` が通っただけでは「LLM が書いた `T ⪱ T + T.Con` インスタンス化が実際に型を通っている」とは限らない（unused import を `lake build` は警告のみ）。以下で具体的に型チェック：

```bash
# .lean 内のインスタンス化を strict に確認
lake env lean S7_E_C2.lean 2>&1 | tee typecheck.log
grep -E "(error|sorry|admit)" typecheck.log && echo "FAIL" || echo "ok"
```

`sorry` や `admit` が含まれていれば即「未達」。

### Step 5: 採用判断

採用条件：
- [ ] `lake build` 通過、`typecheck.log` に error なし、`sorry`/`admit` なし
- [ ] `T ⪱ T + T.Con` インスタンスが具体 `T` で実際に成立
- [ ] §7 forbidden phrases スキャン clean
- [ ] LLM の「未達」項目があれば、それを RESULTS に正直に反映できる形になっている

すべて満たせば **採用**。1 つでも欠ければユーザーに報告して判断を仰ぐ。

### Step 6: 採用時の配置

```
experiments/wp6/
├── README.md           # E-C2 概要、build 手順、§7 文言
└── lean/
    ├── lakefile.toml   # （または .lean）
    ├── lean-toolchain
    └── S7_E_C2.lean    # インスタンス化本体
```

- `RESULTS.md` に E-C2 セクションを追記（claim manifest 形式：claim / status / certificate / experiment id）。GL letterless 階層（E-A2）の「算術側の影」として **構造的にのみ**接続。因果語法・予見語法は使わない。
- `archive/S7_wp6_lean_instantiation/` に LLM 出力を退避（既存 S1/S2 と同じ）。
- `instruction0615/` を `archive/instruction0615/` に退避。
- `docs/integration_notes/wp6_e_c2_lean.md` を新規作成（既存 integration notes パターン踏襲、判断記録）。

### Step 7: CI への組み込み（要判断）

Lean build は数分〜数十分かかる可能性が高い。CI に入れると毎 PR で重くなる。選択肢：

- **入れる**：`make all` と `.github/workflows/test.yml` に Lean build step を追加。確実だが遅い。
- **入れない**：`experiments/wp6/lean/` 配下のみ手動 build。`README.md` で「optional, manual」と明示。WP6 は「optional, stretch task」（指示書 §5）なので入れない選択も妥当。

ユーザーに判断を仰ぐ。

### Step 8: 引き継ぎ（Zenodo 連携）

採用された WP6 E-C2 は次バージョン（v0.2.0）の Zenodo release に含める。CITATION.cff `version` 更新 → tag push → release → 新 DOI 発行。concept DOI は変わらない。

## 重要

- **build が通っていない、または `sorry`/`admit` が含まれているなら、「採用しない」が正解**。指示書 §7「Every claimed theorem carries a prover certificate」を満たさないので。
- **「インスタンスが存在する」と「インスタンスが具体 `T` で型を通っている」は別物**。前者は survey の話、後者が E-C2 の deliverable。
- **Lean 自身の無矛盾性は ZFC に相対化**されている。RESULTS には「絶対的無矛盾性の保証」と書かない。LLM が書いていたら直す。
- **アトリビューション**：Saito (Palalansoukî) / Noguchi (SnO2WMaN) を `experiments/wp6/README.md` に明記。MIT 互換ライセンスかは LLM が確認してくる項目に入れているが、Claude Code 側でも再確認。

## 参考

- 指示書本文：[`02 simspec kether nishida.md`](../../02%20simspec%20kether%20nishida.md) §3 E-C2、§5 WP6、§7 forbidden phrases
- ディスパッチプロンプト：[`prompts/single/S7_wp6_lean_instantiation.md`](../../prompts/single/S7_wp6_lean_instantiation.md)
- 調査結果：[`docs/wp6_survey.md`](../wp6_survey.md)
- 一次ソース：<https://github.com/FormalizedFormalLogic/Foundation/blob/master/Foundation/FirstOrder/Incompleteness/Second.lean>
