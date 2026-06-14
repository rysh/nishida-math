# Zenodo パッケージング — 公開用メタデータ・ドキュメント層の整備

**日付**：2026-06-14
**スコープ**：指示書 §5 WP5 の DoD「Zenodo-ready metadata」「Single-command full reproduction」「manifest lists every claim → artifact path」と §8「Repository (Zenodo-ready: README, CITATION.cff, license, manifest, CI)」「`RESULTS.md`: claim-by-claim with artifact links」を満たすドキュメント層を追加。
**結果**：136/136 通過、`make all` で artifact drift なし、新規 7 ファイル追加。

## 設計判断（変更不可）

### 指示書から一字一句変えずに引いた文言

- **§4-4 epistemic status**: *"illustration, not proof, of the philosophical thesis"* — README banner と RESULTS.md の冒頭に**そのまま**。
- **§4-2 headline 主張**: *"The same diagonal seed launches a strict unbounded hierarchy in one environment and provably nothing in the others."* — README Headline と RESULTS.md に**そのまま**。
- **§8 著者**: "Franny Philos Sophia (Elanare Institute)" — LICENSE、CITATION.cff、.zenodo.json、README 全てに同一表記。

### 指示書 §7 forbidden phrases を避ける

書かなかった：
- 「proves the philosophical thesis」
- 「Nishida anticipated Gödel」
- 「我々の新発見」「初めて示した」等の数学的新規性主張
- 「the constraint generates / causes the ascent」のような因果的一般化（「each `Con_{n+1} → Con_n` is proved」「launches」等、構造的・形式的記述に統一）

「launches」は指示書 §4-2 の原文で用いられている語なので引用部にのみ使用。引用以外では「each stage requires a strictly deeper frame」のように構造的表現に揃えた。

### `claims.json` を変更しない

既存の `claims.json` / `headline_table.md` / `headline_figure.svg` は WP5 で確定済の single source of truth。本タスクではこれらを変更せず、上位レイヤとして RESULTS.md を追加。RESULTS.md は claims.json の人間可読版（§4 metric language）として位置づけ。

### Makefile = CI workflow

`Makefile` の `verify` ターゲットは `.github/workflows/test.yml` と同じ 8 build スクリプト + `git diff --exit-code` を実行する。CI と Makefile のどちらかが drift したら検出可能。

## 追加・変更したファイル

| ファイル | 役割 |
|---|---|
| `README.md` | 新規。epistemic status banner、headline 主張、再現手順、repo map、threats to validity、著者、ライセンス |
| `RESULTS.md` | 新規。3 claim 全てに status + certificate/countermodel path + §4 metric framing |
| `LICENSE` | 新規。MIT 標準テキスト、Copyright (c) 2026 Franny Philos Sophia (Elanare Institute) |
| `Makefile` | 新規。`install` / `test` / `artifacts` / `verify` / `all` ターゲット |
| `CITATION.cff` | 新規。GitHub「Cite this repository」と Zenodo 両対応、ORCID と repo URL は `# TODO` placeholder |
| `.zenodo.json` | 新規。Zenodo GitHub release 連携用 metadata、`license: "MIT"`、`upload_type: "software"` |
| `docs/integration_notes/zenodo_packaging.md` | 本ノート |

## E-A3 Henkin contrast の扱い

指示書 §4-1 triviality objection は (a) Con(F) self-generation と (b) Henkin seed が同じ engine で何も生まないことの 2 段構成。本リポジトリでは (a) は `src/gl/formula.py:con` および `box_power` で実装済（E-A2 ladder の前提）だが、(b) E-A3 は未実装。

README の「Threats to validity」では (a) のみを実装裏付きで主張し、(b) は「Boolos 1993 を参照、本リポジトリでは out of scope」と明記。これにより指示書 §7 forbidden phrases に抵触せず、かつ実装されていない claim を装わない。

## 実走したテスト

```
$ make all
uv sync
Resolved 19 packages in 2ms
Audited 18 packages in 2ms
uv run pytest -q
... (省略) ...
============================= 136 passed in 4.24s ==============================
uv run python experiments/wp3/build_countermodels.py
... (9 countermodel JSON 生成) ...
uv run python experiments/wp3/build_ladder.py
... (9 stages 全て monotone proved / strict refuted / countermodel verified) ...
uv run python experiments/wp3/build_figure.py
uv run python experiments/wp4/e_b1_classical_explosion.py
uv run python experiments/wp4/e_b2_lp_quarantine.py
uv run python experiments/wp5/build_claims.py
uv run python experiments/wp5/build_table.py
uv run python experiments/wp5/build_figure.py
git diff --exit-code
(no output, exit 0)
```

`git status -s` で確認した変更：新規ファイル 6 件のみ（LICENSE、Makefile、README.md、RESULTS.md、CITATION.cff、.zenodo.json）。既存 artifact の決定論性は破れていない。

## WP5 Zenodo DoD 達成状況

| 要件 | 状態 |
|---|---|
| README に epistemic status / headline 主張 / threats to validity を含む | ✅ |
| 単一コマンドの完全再現（指示書 WP5 DoD「Single-command full reproduction」）| ✅ `make all` |
| manifest が claim → artifact path を列挙（指示書 WP5 DoD）| ✅ `RESULTS.md` + `experiments/wp5/artifacts/claims.json` |
| CITATION.cff | ✅ MIT 確定、著者は指示書 §8 通り |
| LICENSE | ✅ MIT |
| .zenodo.json | ✅ |
| CI | ✅ 既存（`.github/workflows/test.yml`）|
| `RESULTS.md`: claim-by-claim with artifact links, in the §4 metric language | ✅ 3 claim 全てに status / certificate / §4 framing |
| Author/credit block: Franny Philos Sophia (Elanare Institute) | ✅ |

## 残ユーザー確認項目

Zenodo に上げる前にユーザーから値が必要：

1. **著者 ORCID** — CITATION.cff の `# TODO: fill in once available` を置換。
2. **連絡先メール** — 任意（Zenodo は必須にしていない）。
3. **GitHub repository URL** — CITATION.cff の `repository-code` を最終値に置換（暫定で `https://github.com/elanare/generative-contradiction` とした）。
4. **最終リポジトリ名・タイトル** — 暫定「Generative Contradiction — A Computational Exhibit」。

確定済み（プラン段階で解決）：ライセンス = MIT、著者表記 = 指示書 §8 通り、公開タイミング = 論文投稿前 DOI 取得。

## 残 WP の扱い

| WP | 状態 |
|---|---|
| WP1〜WP5 | ✅ 完了 |
| WP5 Zenodo パッケージング | ✅ 本タスク |
| WP6（E-C1, E-C2 Lean/Isabelle）| 🛑 後回し（指示書 §5「only if time remains」、§5 priority order 末尾） |
| E-A3 Henkin contrast 実装 | 🛑 out of scope（README で明記、文献参照に留めた）|

論文側執筆（Paper A）、Zenodo 実アップロード、ORCID の確定はユーザー判断で個別実施。
