# WP3 ladder figure 生成

**日付**：2026-06-12
**スコープ**：指示書 §3 E-A2 の headline figure "the ladder" を SVG として生成
**結果**：128/128 通過（既存 99 + 新規 ladder 29）。manifest と SVG は再生成で git diff なし

## 設計判断（変更不可）

### y 軸は最小反例世界数（n+2）単独

x = stage n、y = 最小反例世界数。**letterless 真理集合のカーディナリティを y 軸にする案は不採用**。理由は：

- このプロジェクトが示すのは「矛盾を解消する高次構造を生成しなければならない」という **生成の方向**。意味（self-reference が要求する高次の決定）を伴う次元 n において、各段の矛盾を解消するには、より深い世界構造そのものを生成する必要がある。
- 最小反例深さが線形に伸びることは、その生成性の量的な現れ（指示書 §2.3 末尾「the witness that the hierarchy hasn't collapsed at stage n requires a strictly deeper world-structure. This is the quantitative face of generativity.」）。
- 「規定の真理集合を数え上げる」という測り方（カーディナリティ）は、生成の方向ではなく既存集合の計数になってしまうため、このプロジェクトの主張と合わない。

### letterless reducer は整合性チェック・正規形判定の道具に限定

GL 内部での letterless fragment は完全分類されるが、それは公理系というフレーム内の目盛りであって、意味空間そのものが有限分類されるという主張ではない。growth を集合カーディナリティで測ると、この区別が曖昧になる。よって S2 reducer は Con_n 正規形の機械検証（Task 4 で実装済）と将来の整合性チェックに限定して使う。

## 実装サマリ

### 追加・変更したファイル

| ファイル | 役割 |
|---|---|
| `experiments/wp3/build_countermodels.py` | `max_n` を 4 → 8 に拡張（既存純粋関数は不変） |
| `experiments/wp3/countermodels/strict_n{5..8}.json` | 新規 4 件の countermodel artifact（n+2 worlds、推移閉包込み線形順序、`Imp(Con(n), Con(n+1))` を反証） |
| `src/gl/kripke_search.py` | `enumerate_finite_gl_frames(num_worlds, *, height_bound)` を公開 wrapper として追加（`__all__` 拡張）。内部 `_frames` を直接公開しない |
| `experiments/wp3/build_ladder.py` | 新規。各 stage に prover certificate + 検証済 countermodel を集めて manifest を作る。n ≤ 4 では `enumerate_finite_gl_frames` を使った exhaustive minimality search を実施 |
| `experiments/wp3/build_figure.py` | 新規。matplotlib 経由で SVG を出力。決定論的（hashsalt 固定、font をパス化） |
| `experiments/wp3/artifacts/ladder_manifest.json` | 新規。stage manifest |
| `experiments/wp3/artifacts/ladder_figure.svg` | 新規。headline figure |
| `pyproject.toml` | `[dependency-groups] dev` に `matplotlib>=3.8` 追加 |
| `tests/test_ladder.py` | 新規。29 件のテスト（manifest 形、stage ごとの不変式、figure 決定論性） |
| `docs/integration_notes/wp3_ladder_figure.md` | このノート |

### engine と prover の分離（指示書 §7 準拠）

minimality 検証で frame 上の formula 評価には独立な `gl.countermodel_verifier.verify_countermodel` を呼ぶ。`kripke_search._eval`（engine 内部）は呼ばない。これにより「反例フレームが存在しない」という非導出主張も、prover や reducer 自身ではなく **独立 verifier** で検証される。

## ladder データ（n = 0..8）

| n | 最小反例世界数 | Monotone | Strict | minimality exhaustively checked | frames examined |
|---|---|---|---|---|---|
| 0 | 2 | proved | refuted | ✓ | 1 |
| 1 | 3 | proved | refuted | ✓ | 2 |
| 2 | 4 | proved | refuted | ✓ | 4 |
| 3 | 5 | proved | refuted | ✓ | 11 |
| 4 | 6 | proved | refuted | ✓ | 51 |
| 5 | 7 | proved | refuted | — | — |
| 6 | 8 | proved | refuted | — | — |
| 7 | 9 | proved | refuted | — | — |
| 8 | 10 | proved | refuted | — | — |

n ≤ 4：(n+2)-鎖より小さい全 GL frame を `enumerate_finite_gl_frames` で列挙し、`verify_countermodel` でどれも反例にならないことを確認。加えて `(n+2)`-鎖が反例であることを `verify_countermodel` で独立検証 → **最小反例世界数 = n+2 が exhaustive に確定**。

n = 5..8：(n+2)-鎖の countermodel が `verify_countermodel` で反例として通り、かつ `prove_gl(Imp(Con(n), Con(n+1)))` が `refuted` を返す（理論上 (n+2)-鎖未満では反例不可だが exhaustive search は計算コストの都合で行わず、指示書 §3 E-A2「minimality confirmed n ≤ 4」に従う）。

## 実走したテスト

```
$ uv run pytest tests/test_ladder.py -v
collected 29 items
tests/test_ladder.py .............................                       [100%]
============================== 29 passed in 1.97s ==============================

$ uv run pytest
128 passed in 13.01s
```

既存 99 件 + 新規 29 件 = **128 件通過**。

### 決定論性確認

```
$ uv run python experiments/wp3/build_ladder.py
$ cp ladder_manifest.json /tmp/run1.json
$ uv run python experiments/wp3/build_ladder.py
$ diff -q ladder_manifest.json /tmp/run1.json
(no output → identical)

$ uv run python experiments/wp3/build_figure.py
$ cp ladder_figure.svg /tmp/figure_run1.svg
$ uv run python experiments/wp3/build_figure.py
$ diff -q ladder_figure.svg /tmp/figure_run1.svg
(no output → identical)
```

`tests/test_ladder.py::test_figure_render_is_deterministic` でもバイト一致を機械検証。

## WP3 Definition of Done 達成状況

指示書 §5 WP3 Definition of Done に照らす：

| 要件 | 状態 |
|---|---|
| (Monotone)/(Strict) certified for n ≤ 8 | ✓ manifest に prover status を記録 |
| minimality confirmed n ≤ 4 by exhaustive search | ✓ `enumerate_finite_gl_frames` 経由で確認、frames_examined を記録 |
| Letterless normal-form reducer | ✓ S2 で実装済（Task で別途整合性チェック追加） |
| Output figure "the ladder" | ✓ SVG 出力、決定論的に再生成可能 |

**WP3 は仕上がった**。

## 次タスクへの準備状況（WP5 headline 表）

WP5 は古典 / LP / GL の 3 環境比較表を作る。WP3 で揃ったもの：

- GL 側：Gödelian fixed point が ¬□⊥ に解けて Con₀ ⊊ Con₁ ⊊ ... を launch（ladder manifest + figure 完成）
- LP 側：liar が v(λ)=b で satisfiable、`E-B2` で inertness 確認済（既存 `experiments/wp4/e_b2_lp_quarantine.py`）
- 古典側：liar 充足不可能、vacuous explosion 確認済（既存 `experiments/wp4/e_b1_classical_explosion.py`）

3 要素ともデータ artifact として既に揃っているので、WP5 は 3 つの JSON manifest を読んで headline 表（Markdown または SVG）を組み立てるだけのタスクになる。WP3 ladder manifest を WP5 が参照する場合は `experiments/wp3/artifacts/ladder_manifest.json` の `stages[0].witness_world_count == 2` を「GL: hierarchy launched, minimal witness depth at stage 0 = 2」として要約することになるだろう。
