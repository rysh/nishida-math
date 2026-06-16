# I2: 何段まで登れるか、登れなくなったら理由を持って帰る

> 🎯 これは **Claude Code への探索タスク**（このリポジトリ内 ＋ Lean サブプロジェクト）。
> 主軸は **算術側 Lean（E-C2）を stage 1 から上へ、登れるだけ登る**。
> 従：GL 側 minimality を上へ。
> **本タスクの成果は「天井の段数」と「登れなくなった正確な理由」である。**
> 全段を登りきることが目的ではない。壁の発見そのものが成果。

---

## 動機（正直に）

現状、算術側 Lean（`experiments/wp6/lean/`）は **stage 1 のみ**：
`𝗜𝚺₁ ⪱ 𝗜𝚺₁ + Con(𝗜𝚺₁)`。GL 側は `Con_n` を n=0〜8 まで（minimality は n≤4 まで exhaustive）。
「算術側が一段だけ」というのは、GL 側の梯子に比べて非対称に見える。

ただし **重要な前提**（指示を出す側の判断として明記する）：
- 反復 consistency extension `T + Con(T) + Con(T+Con(T)) + …` を超限まで伸ばすのは
  Turing–Feferman progression そのもので、**limit ordinal での公理 coding** という
  非自明な数学を要する。Foundation がこれを既に持っていれば数段は `inferInstance` で伸びる。
  持っていなければ、stage 2 ですら**自前の新規 formalization** になり、armor のスコープを超える。
- だから本タスクは「**Foundation が提供する範囲で**登れるだけ登り、提供が尽きた地点で止まって、
  なぜ尽きたかを報告する」。**新規 formalization に突入しない**。

## 歯止め（これを破ったら不採用）

- **Foundation（ピン留め commit `c28942b7d9d0df41ee5b736602c3f27b8643532c`）にある補題・
  インスタンスだけを使う。** `sorry` / `admit` / `native_decide` での突破は禁止。
- ある stage が Foundation の既存資産で組めないと判明したら、**そこで止まる**。
  「自分で証明する」に進まない。何時間もかけて新規形式化を試みない。
- 各 stage について、`#print axioms` で公理依存を確認し、新しい公理が増えていないか見る。
- **「通った風を装わない」**：`lake build` を実際に走らせ、exit code を記録する。
  走らせていない／走らせられない場合は「build 未確認」と正直に書く（現状の README が
  そうしているのと同じ規律）。**exit 0 を見ていないのに「通る」と書かない。**

## 依頼

### A. 算術側 Lean を上へ（主軸）

`experiments/wp6/lean/S7Wp6LeanInstantiation.lean` を起点に：

1. **stage 2 を試す**：`(𝗜𝚺₁ + 𝗜𝚺₁.Con) ⪱ (𝗜𝚺₁ + 𝗜𝚺₁.Con) + (𝗜𝚺₁ + 𝗜𝚺₁.Con).Con`
   に相当する term が、Foundation の `T ⪱ T + T.Con`（任意の適格 `T` に対するインスタンス）を
   `T := 𝗜𝚺₁ + 𝗜𝚺₁.Con` に再適用するだけで `inferInstance` で通るか。
   **鍵**：`𝗜𝚺₁ + 𝗜𝚺₁.Con` が、その強化インスタンスの前提
   （`[T.Δ₁]`, `[𝗜𝚺₁ ⪯ T]`, `[Consistent T]`）を Foundation 内で満たすか。
   - `[Consistent (𝗜𝚺₁ + 𝗜𝚺₁.Con)]` は自明には出ない（second incompleteness の核心：
     `𝗜𝚺₁` は自分の無矛盾性を証明できない）。Foundation がこの consistency を
     どういう仮定の下で供給するか（あるいはしないか）が、stage 2 が通るかの分岐点。
     **ここを正確に調べて報告する。**
2. **通るなら stage 3, 4, … と同じ手で伸ばす。** 各 stage で `lake build` の exit code、
   `#print axioms` の差分を記録。
3. **通らなくなったら止まる。** その stage で、Foundation の何が足りないのかを特定：
   - `[Consistent (…)]` インスタンスが供給されないのか
   - `[T.Δ₁]`（Δ₁-definability）が反復理論に対して供給されないのか
   - 型が合わない／名前空間の問題なのか
   - reflection / ordinal-indexed progression が Foundation に**そもそも無い**のか
   この「足りないもの」の正確な名指しが、本タスクの最重要成果。

4. **超限・一般 n の可能性も調べる（机上で可）**：Foundation に、`Con_n` を `n : ℕ` で
   添字づけた反復拡張、あるいは ordinal progression（Turing–Feferman 系）の形式化が
   **存在するか**を、ライブラリを grep して報告。あれば「一般 n まで一気に行ける」可能性、
   なければ「stage 単位の手動反復が天井」と結論。

### B. GL 側 minimality を上へ（従）

`experiments/wp3/` の `Con_n` 階層は n=0〜8、exhaustive minimality は n≤4。

1. minimality の exhaustive 検証を n=5, 6, … と**計算が現実的な範囲で**上げる。
2. 落ちた地点（メモリ／時間で frame 列挙が爆発する n）と、その**計算量的理由**
   （状態空間のサイズ、列挙した frame 数）を記録。
3. これは「天井の理由が**計算量**（GL 側）」と「天井の理由が**ライブラリの数学的範囲**（Lean 側）」
   という、**質の違う 2 つの壁**を対比させる意味がある。両方を報告に含める。

### C. 報告（最重要成果物）

`experiments/wp6/CLIMB_REPORT.md` に：

- **算術側 Lean**：到達した最大 stage、各 stage の `lake build` exit code（または「未確認」）、
  `#print axioms` 差分、そして**止まった理由の正確な名指し**。
- **Foundation 調査**：反復 consistency extension / ordinal progression が Foundation に
  あるか無いか（grep 結果つき）。あれば一般化の道、なければ手動反復の天井。
- **GL 側**：minimality を伸ばせた最大 n、落ちた地点の計算量的理由。
- **結論**：「算術側の天井は stage N で、理由は X」「GL 側の天井は n=M で、理由は計算量」。
  もし stage 1 が天井だったら、それも**正しい結論**として報告する（失敗ではない — 下記）。

## stage 1 が天井でも、それは失敗ではない（指示を出す側の明示）

仮に Foundation の制約で算術側が stage 1 までしか伸びなくても、それは論文の弱点ではない。
理由を報告に**そのまま書いてよい**：

- 論文の哲学的主張は **possible infinity（完成しない開いた継起）**。無限上昇を算術側で
  「完成」させる必要はない。
- 役割分担：**GL 側**（letterless、各段に反例）が「梯子はどこまでも閉じない」を担い、
  **算術側 Lean** は「その一歩が現実の算術理論 `𝗜𝚺₁` で本物だ」を担う。後者は一段で十分機能する。
- したがって「stage 1 が天井、理由は Foundation が反復拡張を ordinal progression として
  持たないから」は、**正しい境界の発見**であって、armor として何も損なわない。

ただし ── もし Foundation が思いがけず数段（あるいは一般 n）を提供していたら、それは
**嬉しい上振れ**。armor が厚くなる。だから「登れるだけ登る」。

## Done の定義

1. 算術側 Lean が、Foundation の既存資産だけで到達できる最大 stage まで伸ばされている
   （`sorry` なし、`lake build` exit code 記録 or「未確認」明記）。
2. 止まった stage の理由が、Foundation の何が足りないかとして**正確に名指し**されている。
3. Foundation に反復拡張／ordinal progression があるか無いかが grep で確認・報告されている。
4. GL minimality が計算現実的な範囲で伸ばされ、落ちた地点の計算量的理由が記録されている。
5. `CLIMB_REPORT.md` に 2 種類の壁（ライブラリ範囲 / 計算量）が対比して報告されている。
6. 新規 formalization に突入していない（歯止めを守った）。
