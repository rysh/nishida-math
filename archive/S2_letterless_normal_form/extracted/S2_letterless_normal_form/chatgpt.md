# §0 自己申告

- 確信度：Medium-High
- 不安な箇所（具体的に）：
  1. 既存 `Formula.to_json()` / `Formula` の内部形状を実際には参照できていないため、`letterless.py` は `type`/`args`/`arg`/`left`/`right`/`to_json()` の複数形状に耐えるようにしているが、未知の独自形状なら微修正が必要。
  2. 仕様の KAT `Not(Box(Not(Box(bot())))) -> Not(box_power(bot(), 2))` は、同じ表の Löb-instance KAT と両立しない。正しい GL-同値先は `Not(box_power(bot(), 1))` と判断し、テストもそのように修正した。
  3. `Hypothesis` 500件はリポジトリ実体なしでは実測できていない。prover の性能次第では `max_size` を下げる必要がある。
  4. interval/rank semantics は closed GL fragment の標準的な計算手続きに基づくが、Boolos 1993 の該当章本文は直接確認していない。
- 参照した文献・URL（あれば）：公開Web検索で見える Čačić/Vuković 2012 の closed GL normal-form theorem 記述、Boolos 書誌情報、および GL/Löb axiom の公開講義ノート等。Boolos 1993 本文そのものは未参照。
- ハルシネーション可能性が高い記述：Boolos 1993 の章番号・節番号・本文上の証明詳細。ここでは挙げない。
- 特別申告：
  - Boolos 1993 の Letterless Normal Form Theorem 章を本当に参照したか：No。公開検索結果・二次資料レベルのみ。
  - reduction 規則の正当性についての確信度：High for the interval/rank calculation; Medium for exact integration with the unknown local `Formula` representation.

# 重要な整合性メモ

Prompt の KAT 行：

```python
Not(Box(Not(Box(bot()))))  ~  Not(box_power(bot(), 2))
```

は、同じ表の Löb-instance KAT と衝突する。

`Not(Box(bot()))` は `Imp(Box(bot()), bot())` と命題論理的に同値なので、

```python
Box(Not(Box(bot())))
```

は

```python
Box(Imp(Box(bot()), bot()))
```

と GL-同値。よって後者を `box_power(bot(), 1)` とする KAT を採用するなら、前者の否定は `Not(box_power(bot(), 1))` でなければならない。

この bundle では KAT を corrected expectation に変更し、別途 `Not(Box(Box(bot()))) -> Not(box_power(bot(), 2))` を追加した。

# pytest status

未実行。リポジトリ本体と `gl.tableau.prove_gl` 実装がこの環境にないため、成功件数は申告しない。

# Files

- `src/gl/letterless.py`
- `tests/test_letterless_kats.py`
- `tests/test_letterless_random.py`
