# S8: WP6 (E-C1) LP 透明真理述語の固定点モデル

> 🎯 これは **単独 LLM タスク**（推奨：ChatGPT GPT-5。KAT 多めで誤りを即検出）。
> ただし **サイレント失敗リスクが中**（不動点計算の実装ミスが KAT を通っても残りうる）。
> 結果が怪しければ triangulate 格上げ。
>
> **前置き**：`_shared/preamble.md` を冒頭に貼る。

---

## 文脈（指示書 §3 E-C1、WP6 表）

> E-C1: Kripke-style fixed-point model for a transparent truth predicate over LP /
> strong-Kleene on a small fragment (liar gets b in the minimal fixed point) —
> first-order upgrade of E-B2.
> WP6 DoD: One machine-checked instance; clearly marked optional.

E-B2（既存・採用済み）は LP の**命題**レベルで「矛盾は隔離され何も生まない（inert）」を示した。
E-C1 はこれを **真理述語 T(·) を持つ言語**へ一段上げ、liar 文 ℓ ↔ ¬T(⌜ℓ⌝) が
**最小不動点で値 b（both）を受け取る**ことを構成し、隔離の構造を「真理の不動点」レベルで見せる。
Kripke 1975 の不動点構成を、評価スキーム＝**LP / strong-Kleene** で小さな有限フラグメントに対し実装する。

これは本体の主軸（GL の生成的階層）に対する **control 側の補強**：真理述語を入れても
LP/SK では liar が b/gap に落ち着くだけで階層は launch されない、という E-B2 の一階版。

## 依頼

### 1. 最小フラグメントの定義

- 有限の原子文 + 真理述語 T(⌜·⌝) + ¬,∧,∨。自己言及は ℓ = ¬T(⌜ℓ⌝)（liar）を必ず含む。
- truth-teller τ = T(⌜τ⌝)、および「ℓ を含む合成」をいくつか（後述 KAT 用）。
- コード化 ⌜·⌝ は有限なので**明示テーブル**でよい（Gödel 数化は不要）。

### 2. 不動点構成（Kripke 1975, 評価スキーム = LP / strong-Kleene）

- 拡張 (E⁺, E⁻)（T の外延・反外延）から開始（空 or 適当な基底）、単調作用素を反復、
  最小不動点に到達するまで回す。3 値：t / f / b（LP, designated = {t,b}）または
  gap 版（strong-Kleene, 値 t/f/n）。**どちらを採るか明示**し、できれば両方。
- 単調性と最小不動点の存在を、有限なので**全列挙**で確認できる形に。

### 3. KAT（既知解。多めに。これが品質保証の主役）

最低限：
- `liar ℓ` → **b**（LP）/ **n**（SK）を最小不動点で受け取る。
- `truth-teller τ` → 最小不動点では未定（b/n）。
- `ℓ ∧ ¬ℓ` → 爆発しない（LP designated 判定が成立しないだけ、他文の値は不変）。
- **inert（一階版）**：ℓ を含む文を足しても、ℓ-free 文の真理値集合が増えない
  （E-B2 の conservativity の真理述語版）。全列挙で確認。
- 古典 2 値では同じ liar が不動点を持たない（収束しない/振動する）ことの対比。

各 KAT は「入力 → 期待値 → 実測値」を JSON artifact に落とす。

### 4. 本体 artifact 形式との整合

- 可能なら `_shared/preamble.md` の Formula JSON を真理述語付きに最小拡張して使う
  （`{"type":"T","arg":<code>}` のような追加）。拡張したらスキーマ差分を明記。
- 出力 artifact は `experiments/wp6/artifacts/e_c1_*.json` 想定。

### 5. RESULTS 文言案（§7 厳守）

- これは Kripke 1975 の**既知構成のインスタンス**であり新規数学ではない。
- E-B2 の一階版＝control 補強。本体（生成的階層）と対比的にのみ言及。
- 禁止表現・引用語法（§7）。

## 出力形式

````
## 結論（3 行）

## 設計（フラグメント定義／採用スキーム LP or SK or both）

## コード（全文、純粋関数中心、Python 3.12）

## KAT 一覧（入力→期待→実測、最低 6 個）

## artifact サンプル（JSON）

## スキーマ拡張差分（あれば）

## RESULTS 文言案（§7 準拠）

## 不明・自信のない箇所（§0 申告）
````

## 重要

- **最小不動点であることを全列挙で確認**（「不動点の一つ」ではなく最小)。
- liar が b/n に落ちるのは「矛盾の隔離」であって「生成」ではない——この対比を曖昧にしない。
- 3 値の設計（LP designated={t,b} と SK gap=n）を混同しない。**どちらか明示、できれば両方**。
- 指示書 §7 を全文チェック。自信のない箇所は正直に。

Claude Code は受領後：(1) 不動点の最小性と単調性を独立に全列挙検証、
(2) KAT を本リポジトリ側で再実行、(3) inert（一階版）を確認、(4) §7 スキャン、
(5) 採用なら `experiments/wp6/` 配置・`RESULTS.md` 補遺・`archive/S8_wp6_lp_truth_predicate/` 退避。
