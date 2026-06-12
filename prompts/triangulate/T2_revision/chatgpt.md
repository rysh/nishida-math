# T2 修正依頼（ChatGPT 宛、同じスレッドで続けて貼る）

前回の T2 提出（k-decomposition による fixed_point + path-based alt + AST 分離テスト）を Claude Code が
受け取り、リポジトリに統合する手前で精査しました。**実装の骨格は採用候補です**。
ただし、以下の点を確認・修正してください。修正後はもう一度 zip で出してください。

## 1. 実行環境の確認（最重要）

前回「`prove_gl` が手元に無いため未実行」と書きましたね。実行のための情報を以下に渡します。
今度は **実走させて `X passed` を確実に申告** してください。

リポジトリトップで：

```bash
uv run pytest -q
```

src tree（重要なものだけ抜粋）：

```
src/gl/__init__.py             # 空
src/gl/formula.py              # Formula, ProofResult, bot(), atom(), Not(), And(), Or(),
                               # Imp(), Iff(), Box(), box_power(), con(), atoms(), subformulas(),
                               # modal_depth(), pretty(), modal_subformulas() を export
src/gl/tableau.py              # prove_gl(formula: Formula) -> ProofResult
src/gl/kripke_search.py        # prove_gl(formula: Formula) -> ProofResult
src/gl/countermodel_verifier.py # verify_countermodel(formula, model_json) -> bool
```

`ProofResult.status` は `"proved"` または `"refuted"`。
`pyproject.toml` には `pythonpath = ["src"]` と `testpaths = ["tests"]` が既設なので、
あなたのテストの `from gl.fixed_point import ...` はそのまま動くはずです。
依存関係に `hypothesis>=6.100` も追加済み。

## 2. `Box(⊤) → ⊤` 簡約の境界線について

§0 自己申告で「engine 内で正しさを判定しない要件と境界線」と書いていました。実は **`Box(Not(bot())) ≡ Not(bot())`（GL ⊢ □⊤）** は GL の定理であり、これを engine 内で
構文簡約として行うのは **engine が判定器を持っていることにはなりません**（Boolos アルゴリズムでの正規化に含まれる範囲です）。
ただし、これが Henkin KAT の期待形をきれいに出すために**必須かどうか**だけ確認したいです：

- `_simplify` を完全に外して、Henkin KAT `fixed_point(Box(atom("p")), "p")` で何が返るか
- そのとき `prove_gl(Iff(returned_H, Not(bot()))).status == "proved"` か

もし `_simplify` なしでも独立 prover が equivalence を pass させるなら、`_simplify` を **`Box(⊤)→⊤` だけは残して他は最小化**してください（constant folding は OK、`Imp` の `left == right` 等の同値変形は外す）。
理由：レビュー時に「engine が GL の同値変形を肩代わりしている」と疑われる余地を減らすためです。
もし `_simplify` 必須なら、その判断と理由を `fixed_point.py` の docstring に明記してください。

## 3. 第 2 アルゴリズム（alt）の独立性

§7 で「主実装と alt は同じ k-decomposition 定理に基づく」と認めています。
これは uniqueness テストの価値を下げます。可能であれば、alt は **本当に別系統** にしてください。
たとえば：

- **trace / rank-based**：letterless fragment 用の S2 実装に近い rank semantics で、p を含む式を「p に関する rank function」に変換し、固定点を rank 0 で評価して値を抜き出す
- または、**Bernardi uniqueness 経由**：「H ↔ A(H) を満たし、p を含まない式」を有限候補集合から brute-force で探索（深さ・サイズで bounded）、最初に GL prover が pass させたものを返す

後者は engine の中で `prove_gl` を呼ぶことになるので **NG**。前者の rank-based に挑戦する余地があるか
検討してください。もし時間的に難しければ「alt は同系統で uniqueness テストは構造的差分の sanity check として機能する」と
docstring に明記して残してください。

## 4. random battery の規模

前回 `max_examples=225` でした。dispatch は「≥ 200」と書いたのでギリギリ満たしていますが、
**実走したときの timeout** が prover 性能に依存します。実走した結果、どれくらいかかったかと、
hypothesis が実際に何例消化したかを報告してください。

## 5. 既存テストへの影響

統合先のリポジトリには既に **26 件の pytest が通っています**（GL prover, LP, classical）。
あなたの追加分を入れて 26 件が壊れていないこと、新規分が通っていることを `uv run pytest -v` で
確認し、件数と内訳を報告してください。

## 提出形式

前回と同じ zip、ただし以下を追加：

- `RESULTS.md`（または README に追記）：実走確認の `X passed` の内訳、上記 2/3 への回答、
  random battery の所要時間と消化数
- `_simplify` を縮小した場合：縮小版のコード
- alt を別系統にできた場合：rank-based 等の概要

期限：可能な限り早めにお願いします。並行して他タスクの統合を進めます。
