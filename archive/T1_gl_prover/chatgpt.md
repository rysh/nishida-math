実装一式を zip にまとめました。

[gl_prover_submission.zip](sandbox:/mnt/data/gl_prover_submission.zip)

## 内容

含めたファイルは指定どおりです。

```text
src/gl/formula.py
src/gl/tableau.py
src/gl/kripke_search.py
src/gl/countermodel_verifier.py
tests/test_gl_kats.py
tests/test_gl_random.py
pyproject.toml
```

## 検証結果

ローカルで以下を実行し、通過しました。

```bash
cd /mnt/data/gl_prover_submission
uv run pytest -q
```

結果：

```text
15 passed
```

内訳は、KAT 群と Hypothesis による random battery です。`tests/test_gl_random.py` は `max_examples=1000` で、モーダル深さ ≤ 3、原子 `p/q/r` の式について、方法 A と方法 B の status 完全一致、および反例モデルの独立検証を行います。

## 実装方針

GL の有限フレーム側は、有限 GL-frame を transitive + irreflexive frame として扱っています。これは GL の標準的な Kripke semantics と整合しており、有限 GL-frame が transitive irreflexive frame として記述されること、また GL が有限 GL-frame に関して sound/complete とされることに基づく設計です。([homepage.mi-ras.ru][1])

方法 A の `src/gl/tableau.py` は、`F φ` から始める signed labelled tableau です。古典 α/β 規則、`T□A` の全後続世界への伝播、`F□A` の witness world 生成、推移性を保つ predecessor-closed edge 追加、反射辺禁止を入れています。GL 固有の有限化は、exact world-signature loop 検出と modal-depth guard の二段で扱っています。

方法 B の `src/gl/kripke_search.py` は、rooted finite transitive irreflexive frame を world 数昇順で列挙します。root を 0 とする topological normal form を使い、全 world が root から到達可能な成分だけを列挙します。chain height は `modal_depth(formula)` で制限し、world bound は `1 + #distinct box subformulas` にしています。

`src/gl/countermodel_verifier.py` は、証明器側の評価関数を呼ばず、Formula JSON を直接評価して、transitive / irreflexive / root refutation を別経路で確認します。

## §7: 差が出やすい論点への明示回答

1. **ループ検出のシグネチャ定義**
   `tableau.py` の `_gl_loop_reason` で、各 world の signature を「その world 上の全 signed formula の exact set」と定義しています。ancestor と descendant の exact signature が一致し、descendant に未処理の `F□A` が残っている場合だけ閉枝にします。これは aggressive な subsumption ではなく、誤閉枝を避けるための保守的実装です。

2. **Löb 規則の扱い**
   Löb 公理を逆向きに rewrite する規則は入れていません。`□(□A→A) → □A` は、GL tableau の witness 生成、`T□` 伝播、loop/depth closure によって閉じます。つまり Löb を「公理として直接展開」するのではなく、GL-frame 条件から閉じる設計です。

3. **modal subformula property の使いどころ**
   方法 B で `1 + #distinct box subformulas` を finite search の world bound として使っています。方法 A では tableau 展開対象は input 由来の subformula とその signed 分解に限定され、`F□A` witness 生成時にも principal formula の arg だけを降ろします。

4. **反例モデル抽出時の world ordering**
   tableau 反例は生成順 world id をそのまま使います。Kripke search 側は root `0`、topological order `0 < 1 < ...` で列挙します。n=0 strictness KAT の `Con_0 → Con_1` では、方法 B が最小反例 `worlds=[0,1]`, `rel=[[0,1]]` を返すようにしています。

## 不確かさ・統合時に確認すべき点

`tableau.py` の certificate は JSON-serializable な閉枝木ですが、既存リポジトリ側に厳密な certificate schema がある場合は adapter が必要です。

方法 B の world bound は実用的な filtration-style bound として実装しています。既存の GL 証明器が別の既定 bound、たとえば closure size 全体や Fischer-Ladner closure を使う設計なら、`_default_world_bound` だけ差し替えるのが統合上いちばん安全です。

これは展示用の計算的 illustration 実装であり、プロジェクトの哲学的テーゼを proof するものではありません。

[1]: https://homepage.mi-ras.ru/~sk/lehre/penn2017/GL_slides.pdf?utm_source=chatgpt.com "Gödel – Löb Provability Logic"
