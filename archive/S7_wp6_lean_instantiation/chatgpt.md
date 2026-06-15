## §0 自己申告

* 確信度：**Medium**

* 不安な箇所：

  1. **`lake build` は未確認**。この実行環境には `lean` / `lake` がなく、コンテナ側の外部ネットワークも DNS 解決に失敗したため、実機ビルドはできていない。
  2. **`ISigma 1` の `Δ₁`-definability は Foundation 側で axiom 扱い**。`Examples.lean` に `axiom ISigma1_delta1Definable : ...` があり、それを instance として登録している。これは `sorry` ではないが、Lean の trusted axiom として入る点を成果物で明示すべき。([GitHub][1])
  3. **`lakefile.toml` の依存解決は未実行**。Lake の TOML 依存指定としては `git` + `rev` が公式に記載されているが、Foundation 依存込みの `lake update` / `lake build` は未確認。([Lean Language][2])
  4. **GitHub HTML 表示で一部 Unicode notation が欠落して見える**。そのため `.lean` 本体では `₁` ではなく ASCII 名 `ISigma 1` を使ってリスクを下げた。
  5. **Foundation master の最新性**。アクセスできた GitHub commit page では `c28942b7d9d0df41ee5b736602c3f27b8643532c` を確認し、再現性のためここに pin した。([GitHub][3])

* 参照した文献・URL：

  * FormalizedFormalLogic/Foundation repository。README は Foundation が Lean 4 による mathematical logic formalization であり、First-Order Arithmetic に Gödel 第一・第二不完全性定理を含むと記載している。([GitHub][4])
  * `Foundation/FirstOrder/Incompleteness/Second.lean`。`consistent_unprovable` と `instance [Consistent T] : T ⪱ T + T.Con` を確認した。([GitHub][5])
  * `Foundation/FirstOrder/Incompleteness/Examples.lean`。`ISigma1_delta1Definable` axiom と `instance : ... ⪱ ... + ...Con := inferInstance` を確認した。([GitHub][1])
  * `Foundation/FirstOrder/Arithmetic/Schemata.lean`。`ISigma` の定義、`ISigma 1` 近傍の notation、`models_ISigmaOne` と consistency instance を確認した。([GitHub][6])
  * Foundation pinned commit の `lean-toolchain` と `lake-manifest.json`。Lean toolchain は `leanprover/lean4:v4.29.0`、Mathlib は `1a37cd3c8e618022c5e78dee604c75c3c946a681`。([GitHub][7])
  * Foundation README の開発者表記。Palalansoukî = Shogo Saito、SnO2WMaN = Mashu Noguchi。([GitHub][4])

* ハルシネーション可能性が高い記述：

  * `lakefile.toml` が Foundation 依存をこのまま完全解決できるか。
  * `ISigma 1` を使った下記 theorem がローカル `lake build` でそのまま通るか。
  * stage 1→2 の明示 theorem。Foundation `Examples.lean` には stage 1→2 らしき instance が見えるが、GitHub HTML/抽出表示で RHS が欠落して見えるため、本成果物では deliverable に含めない。([GitHub][1])

---

## 結論（3 行：何を 1 インスタンス検証したか／build 状況／未確認事項）

* 基底理論を `LO.FirstOrder.Arithmetic.ISigma 1` とし、`ISigma 1 ⪱ ISigma 1 + (ISigma 1).Con` を Foundation の既存 instance から呼び出す最小 `.lean` を提示する。
* これは `Second.lean` の `T ⪱ T + T.Con` 汎用 instance と、`Examples.lean` の `ISigma 1` 用 `Δ₁` instance を使うインスタンス化である。([GitHub][5])
* **この回答内では `lake build` 未確認**。stage 1→2 は未達として扱う。

---

## 環境

* lean-toolchain: `leanprover/lean4:v4.29.0`。([GitHub][7])
* Foundation commit: `c28942b7d9d0df41ee5b736602c3f27b8643532c`。([GitHub][3])
* Mathlib version: Foundation manifest 上の `mathlib4` rev は `1a37cd3c8e618022c5e78dee604c75c3c946a681`。([GitHub][8])

`lean-toolchain`:

```text
leanprover/lean4:v4.29.0
```

`lakefile.toml`（全文）:

```toml
name = "S7Wp6LeanInstantiation"
defaultTargets = ["S7Wp6LeanInstantiation"]

[leanOptions]
pp.unicode.fun = true
weak.linter.flexible = true
weak.linter.refine = true
weak.linter.oldObtain = true
weak.linter.style.multiGoal = true

[[require]]
name = "Foundation"
git = "https://github.com/FormalizedFormalLogic/Foundation.git"
rev = "c28942b7d9d0df41ee5b736602c3f27b8643532c"

[[lean_lib]]
name = "S7Wp6LeanInstantiation"
```

---

## E-C2 本体 .lean（全文、コメントつき）

ファイル名案：`S7Wp6LeanInstantiation.lean`

```lean
import Foundation.FirstOrder.Incompleteness.Examples

/-!
WP6 E-C2 / stage 1 arithmetic-side instantiation.

This file does not re-formalize incompleteness.
It imports Foundation's existing incompleteness development and asks Lean
to synthesize one concrete instance for the base arithmetic theory `ISigma 1`.

Important dependency note:
`Foundation.FirstOrder.Incompleteness.Examples` provides the instance
for `(ISigma 1).Δ₁` via `ISigma1_delta1Definable`.
In Foundation at the pinned commit, this is an axiom, not a derived theorem.
-/

namespace LO.FirstOrder.Arithmetic

open LO.Entailment

/--
Type-level sanity check 1:
the chosen base theory has the `Δ₁` definability instance needed by
`consistent_unprovable` / `T ⪱ T + T.Con`.

At the pinned Foundation commit this comes from
`ISigma1_delta1Definable` in `Incompleteness.Examples`.
-/
example : (ISigma 1).Δ₁ := by
  infer_instance

/--
Type-level sanity check 2:
the chosen base theory is at least `ISigma 1`.

For `T = ISigma 1`, this is the reflexive/weaker-than instance required
by the generic second-incompleteness theorem in `Second.lean`.
-/
example : (ISigma 1) ⪯ (ISigma 1) := by
  infer_instance

/--
Type-level sanity check 3:
Foundation supplies consistency of `ISigma 1`, via the standard natural-number
model/soundness route in the arithmetic schemata development.
-/
example : Consistent (ISigma 1) := by
  infer_instance

/--
WP6 E-C2, stage 1.

`ISigma 1` is strictly weaker than `ISigma 1 + Con(ISigma 1)`.

Meaning: for `T = ISigma 1`, `Con(T)` is not provable in `T` but is
provable in `T + T.Con` by the added axiom; hence the extension is a genuine
strengthening. This is the arithmetic-side shadow of the GL-side `Con_n`
hierarchy used in E-A2.
-/
theorem wp6_ec2_stage1_ISigma1 :
    (ISigma 1) ⪱ (ISigma 1) + (ISigma 1).Con := by
  infer_instance

end LO.FirstOrder.Arithmetic
```

---

## build ログ（通ったなら要約、通らない／未確認なら正直に）

未確認。

この回答作成環境では以下の理由で `lake build` を実行できなかった。

```text
lean: not available
lake: not available
external network from container: DNS resolution failed
```

したがって、ここでは **build が通ったとは主張しない**。

Claude Code 側で確認する最小手順案：

```bash
lake update
lake build
```

想定される成功条件：

```text
Build completed successfully.
```

ただし、このログは未取得であり、上記は確認手順であって実行結果ではない。

---

## RESULTS 文言案（§7 準拠、3〜5 行）

WP6 E-C2 は、Foundation に収録済みの Saito–Noguchi らの不完全性 formalization を、基底理論 `ISigma 1` に対してインスタンス化する optional artifact である。
得られる `ISigma 1 ⪱ ISigma 1 + (ISigma 1).Con` は、本体 E-A2 の GL 側 `Con_n` 階層と、同一現象の二つの現れとして構造的に対応する。
これは既知結果のインスタンス化による形式的裏付けであり、新規数学的主張ではない。
Lean 検証は Lean / 依存ライブラリ / 基盤理論の健全性に相対化され、絶対的な無矛盾性保証ではない。

---

## 落とし穴自己点検（チェックリストへの回答）

* 基底 `T` が `[Consistent T]` 系 instance の前提を満たすか：

  * `T = LO.FirstOrder.Arithmetic.ISigma 1` を採用。
  * `[T.Δ₁]` は `Examples.lean` の `ISigma1_delta1Definable` による instance。ここは axiom であるため、明示的に申告した。([GitHub][1])
  * `[ISigma 1 ⪯ T]` は `T = ISigma 1` の reflexive/weaker-than instance として type-level sanity check に含めた。
  * `[Consistent T]` は Foundation の arithmetic schemata 側で `ISigma` の標準モデル instance と consistency instance が見える。([GitHub][6])

* commit ピン留め：

  * Foundation を `c28942b7d9d0df41ee5b736602c3f27b8643532c` に pin した。([GitHub][3])
  * Foundation pinned manifest 上の Mathlib rev も記録した。([GitHub][8])

* API 名：

  * `StrictlyWeakerThan` / `⪱`、`T.Con`、`consistent_unprovable`、`Theory.add_def` は `Second.lean` の確認済み表記に合わせた。([GitHub][5])
  * `.lean` 本体では Unicode notation 欠落リスクを避けるため、`₁` ではなく `ISigma 1` を使用した。

* 再 formalize 禁止：

  * 不完全性定理を再構成していない。
  * `infer_instance` により Foundation の既存 instance を呼んでいる。

* ライセンス／アトリビューション：

  * Foundation は README 上で Apache-2.0 license と表示されている。([GitHub][4])
  * アトリビューション：Saito = Palalansoukî / Shogo Saito、Noguchi = SnO2WMaN / Mashu Noguchi。([GitHub][4])

---

## 不明・未達（正直に列挙）

* `lake build` は未確認。
* `lake update` によって生成される downstream project 側 `lake-manifest.json` は未生成。
* stage 1→2 の theorem は deliverable に含めていない。Foundation `Examples.lean` には該当しそうな instance があるが、表示抽出上 RHS が欠落しており、ローカルビルドなしで採用するのは避けた。([GitHub][1])
* `ISigma1_delta1Definable` が axiom である点は、WP6 の「既存ライブラリのインスタンス化」としては使用可能だが、成果物説明では必ず明記すべき。
* Foundation master のさらに新しい commit が存在する場合、この pin は最新ではない可能性がある。ただし再現性のため、本成果物では上記 commit に固定する。

[1]: https://github.com/FormalizedFormalLogic/Foundation/blob/master/Foundation/FirstOrder/Incompleteness/Examples.lean "Foundation/Foundation/FirstOrder/Incompleteness/Examples.lean at master · FormalizedFormalLogic/Foundation · GitHub"
[2]: https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/?utm_source=chatgpt.com "Lake"
[3]: https://github.com/FormalizedFormalLogic/Foundation/commit/c28942b7d9d0df41ee5b736602c3f27b8643532c "chore(deps): bump actions/upload-pages-artifact from 4 to 5 (#820) · FormalizedFormalLogic/Foundation@c28942b · GitHub"
[4]: https://github.com/FormalizedFormalLogic/Foundation "GitHub - FormalizedFormalLogic/Foundation: Formalization of Mathematical Logic · GitHub"
[5]: https://raw.githubusercontent.com/FormalizedFormalLogic/Foundation/c28942b7d9d0df41ee5b736602c3f27b8643532c/Foundation/FirstOrder/Incompleteness/Second.lean "raw.githubusercontent.com"
[6]: https://github.com/FormalizedFormalLogic/Foundation/blob/master/Foundation/FirstOrder/Arithmetic/Schemata.lean "Foundation/Foundation/FirstOrder/Arithmetic/Schemata.lean at master · FormalizedFormalLogic/Foundation · GitHub"
[7]: https://raw.githubusercontent.com/FormalizedFormalLogic/Foundation/c28942b7d9d0df41ee5b736602c3f27b8643532c/lean-toolchain "raw.githubusercontent.com"
[8]: https://raw.githubusercontent.com/FormalizedFormalLogic/Foundation/c28942b7d9d0df41ee5b736602c3f27b8643532c/lake-manifest.json "raw.githubusercontent.com"
