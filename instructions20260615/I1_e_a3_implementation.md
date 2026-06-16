# I1: E-A3 の実装 — Henkin 種は flatline、Gödel 種は launch（機械検証）

> 🎯 これは **Claude Code への実装タスク**（このリポジトリ内で作業）。
> 単独 LLM への外注ではない。既存の GL 証明器・反例検証器を使って、
> **E-A3 を artifact として実在させる**。
>
> **背景**：S5（`prompts/single/S5_e_a3_adversarial.md`）で E-A3 の *敵対的レビュー* は
> 済んでいる。だが E-A3 の **実装は存在しない**（`RESULTS.md` Claim 3 末尾に
> 「E-A3 は本リポジトリでは未実装、out of scope、Boolos 1993 を文献参照」と明記されている）。
> 一方、論文 `paper_draft.md` の §8 は E-A3（Henkin 種 vs Gödel 種の対比）を
> **「機械検証した計算的対応物」として記述している**。これは論文と実装の不一致であり、
> 査読者が companion を覗けば気づく。本タスクはこの穴を塞ぐ。

---

## なぜこれが最優先か（正直な動機）

論文 §8 の中心的主張はこうである：

> 同じ diagonal construction で作った 2 つの自己言及種を比べる。Gödel 種（自分の**不**証明
> 可能性を主張＝¬□p の固定点）は階層を起動する。Henkin 種（自分の証明可能性を主張＝□p の
> 固定点）は、Löb の定理により ⊤ に解け、足しても何も生まない。差は否定一つ。生成するのは
> 自己言及そのものでも矛盾そのものでもなく、**負の自己言及が開くギャップ**である。

この対比が、論文の「generation does not require contradiction（生成に矛盾は要らない）」という
核心命題の**計算的裏付け**になっている。ところが現状その対比は実装されていない。
**論文が「検証した」と言っているものを、実在させる**のが本タスク。

## 不変式（破ったら不採用 — `prompts/_shared/preamble.md` と同じ精神）

- 出力するコード・artifact は、本リポジトリの既存検証規律（プロンプトと反例検証器の分離、
  CI の `git diff --exit-code`）に従って初めて採用される。
- すべての claim は計算的に検証可能な形（テスト、列挙 artifact、反例 JSON）で示す。
- **禁止表現**（`RESULTS.md`「Epistemic status」と同じ）：
  1. シミュレーションが哲学的テーゼを「証明する」
  2. 西田が Gödel を「予見した」
  3. 数学的内容への新規性主張（Boolos 1993, de Jongh–Sambin, Solovay 1976, Priest 1979 は既知）
- **既知の数学である**ことを明記する。Henkin 文と Löb の定理（`□p → p` の固定点が ⊤ に解ける）
  は Boolos *The Logic of Provability* (1993) の標準的内容。新規性は実装と検証であって数学ではない。
- **「通った風を装わない」**：実装が部分的にしか動かない、あるいは GL 証明器が Henkin 種を
  期待通りに簡約しない場合、それを正直に報告する。失敗の正確な報告は成果の一部。

## 依頼

### 1. 実装本体（`experiments/wp3/` または新規 `experiments/wp3a/` に E-A3 として）

既存の GL スタック（`src/gl/`：`formula.py` の `con` / `box_power`、証明器、
`countermodel_verifier.py`）を**再利用**して、以下を機械検証する：

- **Gödel 種**：`H ↔ ¬□H`（既存の固定点機構で構成）が `¬□⊥ ≡ Con_0` に簡約されること。
  そして `Con_0` を足すと E-A2 の階層（既存の `ladder_manifest.json`）が起動すること
  ── これは既存実装の再利用で示せるはず。**既存 E-A2 への接続を明示**。
- **Henkin 種**：`K ↔ □K`（自分の証明可能性を主張する固定点）が、GL において `⊤` と
  同値になること（Löb の定理の帰結）を、GL 証明器で**機械検証**する。すなわち
  `GL ⊢ (K ↔ □K) → K` あるいは同値に `GL ⊢ □K ↔ ⊤` に相当する判定を証明器で出す。
  正確な定式化は証明器の API に合わせてよいが、**「Henkin 固定点 = ⊤」を証明器の出力で
  裏づける**こと。
- **足しても何も生まれない（flatline）**：`F + K`（K を公理として足す）が `F` に対して
  **新しい letterless 定理を生まない**ことを示す。E-A2 の strict 階層（`Con_n → Con_{n+1}`
  が各段で refuted）と**対比可能な形**で。理想は：E-A2 と同じ measure（letterless fragment の
  新規定理、または Kripke 反例の深さ）で測り、Gödel 種は「深さが n+2 で増える」、
  Henkin 種は「増えない（flatline）」を**同一の物差し**で出すこと。

### 2. 同一エンジン・同一物差しの担保（これが E-A3 の肝）

E-A3 の主張は「**同じ** diagonal operator、差は負の自己言及だけ」である。だから：

- Gödel 種と Henkin 種は、**同じ固定点構成コード**（`src/gl` の同じ関数）から作ること。
  別々のアドホックな構成にしない。差が `¬□p` vs `□p`（否定一つ）だけであることを
  コード上で可視化する。
- 生成の有無は、**同じ measure** で測る（E-A2 が使っている letterless fragment の
  consequence、または反例チェーンの深さ）。Gödel 側と Henkin 側で物差しを変えない。
- 「launch / flatline」を JSON artifact で出す。例：
  `{ "godel_seed": {..., "launches": true, "depth_growth": "n+2"},
     "henkin_seed": {..., "launches": false, "reduces_to": "⊤"} }`

### 3. テストと検証規律

- KAT（known-answer tests）を `tests/test_e_a3.py` に追加：
  Henkin 固定点が ⊤、Gödel 固定点が Con_0、flatline、launch を各々アサート。
- 反例・証明は既存の二重チェック規律に乗せる（証明器が出した判定を、可能なら反例検証器で
  独立確認）。**証明器コードと検証コードの分離**（既存テストの AST import チェック）を壊さない。
- `make all` で artifact が再生成され、`git diff --exit-code` が通ること（決定論的再現）。

### 4. RESULTS.md の更新（§7 厳守、3〜6 行）

- Claim 3 末尾の「E-A3 は未実装、out of scope」を、**実装済みの記述に差し替える**。
- 新 Claim（E-A3）として：Henkin 種 = ⊤（flatline）、Gödel 種 = Con_0（launch）、
  同一エンジン・同一物差し、を artifact パスつきで。
- これは Boolos 1993 の**既知の数学のインスタンス化・検証**であり新規数学ではない、と明記。
- §4 metric 言語で：Henkin 種の generativity = **zero**、Gödel 種 = **unbounded (n+2)**。
  これにより「生成の active ingredient は矛盾ではなく負の自己言及のギャップ」を
  **計算的に**（哲学的にではなく）示した、と書く。「哲学的テーゼを証明した」とは書かない。

### 5. 落とし穴の自己点検

- GL 証明器が Henkin 固定点を ⊤ に簡約できない場合 ── API の制約か、定式化の問題か、
  正直に切り分けて報告。`□K ↔ ⊤` を直接判定できないなら、`GL ⊢ K`（K 自体が定理）を
  示す経路でもよい（Löb：`GL ⊢ □K → K` かつ自明に `K → □K` の固定点なので `GL ⊢ K`）。
  **どの経路で示したかを明記**。
- 「flatline」の measure が E-A2 と完全に同一にできない場合、どこがどう違うかを明記。
  物差しがズレると E-A3 の「同一エンジン同一物差し」主張が崩れるので、ここは特に正直に。

## 成果物の置き場所

- 実装：`experiments/wp3a/`（または `experiments/wp3/` 内に e_a3 として）
- テスト：`tests/test_e_a3.py`
- artifact：`experiments/wp3a/artifacts/e_a3_*.json`
- `RESULTS.md` の Claim 3 / 新 Claim 更新
- 作業ログ（どの経路で Henkin=⊤ を示したか、measure の同一性、未達があればそれ）を
  `experiments/wp3a/NOTES.md` に。

## Done の定義

1. Henkin 種 = ⊤（flatline）が GL 証明器で機械検証されている。
2. Gödel 種 = Con_0（launch）が示され、既存 E-A2 階層に接続されている。
3. 両者が同一固定点エンジン・同一物差しで比較されている。
4. テストが通り、`make all` 後 `git diff --exit-code` が通る。
5. `RESULTS.md` が実装済みに更新され、§7 禁止表現に違反しない。
6. 未達・近似・経路選択がすべて `NOTES.md` に正直に記録されている。
