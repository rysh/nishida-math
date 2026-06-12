## §0 自己申告

* **確信度**：Medium-High

* **不安な箇所**：

  1. 既存 `Formula` / `to_json()` の実装詳細を実ファイルで確認できていないため、`letterless.py` は複数の典型形状に耐えるように書いたが、独自表現なら微修正が必要。
  2. 提示 KAT の `Not(Box(Not(Box(bot())))) -> Not(box_power(bot(), 2))` は、同じ表の Löb instance KAT と両立しないため、正しい期待値を `Not(box_power(bot(), 1))` として実装した。
  3. `Hypothesis` 500件は、実リポジトリと `gl.tableau.prove_gl` が手元にないため実走できていない。prover が遅い場合は `max_size` の調整が必要。
  4. Boolos 1993 の該当章本文は直接参照していない。公開検索で確認できる二次資料・抜粋レベルに依拠している。

* **参照した文献・URL（あれば）**：

  * Čačić/Vuković の closed GL fragment normal form theorem 記述。letterless GL sentence が `□^i⊥` の truth-functional combination に正規化される旨と、一意表現の形が述べられている。([Hrčak][1])
  * MIT の Boolos bibliography。`The Logic of Provability` が Cambridge University Press, 1993 として listed。([MIT Philosophy][2])
  * GL の公理系、特に Löb axiom `□(□φ → φ) → □φ` の確認用公開ノート。([バークレー大学数学科][3])

* **ハルシネーション可能性が高い記述**：

  * Boolos 1993 の章番号・ページ番号・証明本文の細部。ここでは主張しない。
  * 既存 `Formula` 実装の内部フィールド名。コード側で複数候補に対応したが、実ファイル未確認。

* **特別申告**：

  * Boolos 1993 の Letterless Normal Form Theorem 章を本当に参照したか：**No**。
  * reduction 規則の正当性についての確信度：**interval/rank semantics と `□` の first-gap 計算は High**。ただし、未知のローカル `Formula` 表現との完全互換性は **Medium**。

成果物 ZIP を作成しました。

[Download `S2_letterless_normal_form.zip`](sandbox:/mnt/data/S2_letterless_normal_form.zip)

中身は以下です。

```text
S2_letterless_normal_form/
├── chatgpt.md
├── src/gl/letterless.py
└── tests/
    ├── test_letterless_kats.py
    └── test_letterless_random.py
```

重要点として、提示 KAT のこの行は修正しています。

```python
Not(Box(Not(Box(bot()))))  # expected Not(box_power(bot(), 1))
```

理由は、`Not(Box(bot()))` と `Imp(Box(bot()), bot())` が命題論理的に同値なので、

```python
Box(Not(Box(bot())))
```

は Löb-instance KAT の

```python
Box(Imp(Box(bot()), bot()))
```

と GL-同値になるためです。したがって後者を `box_power(bot(), 1)` と期待するなら、その否定は `Not(box_power(bot(), 1))` になります。`Not(box_power(bot(), 2))` を期待する別 KAT としては、ZIP 内で

```python
Not(Box(Box(bot())))
```

を追加しています。

実装方針は、closed GL fragment を自然数 rank 上の有限 interval set として評価し、`B_n = □^n⊥` を初期区間 `{0, ..., n-1}` と見ます。Boolean connective は interval set 演算、`Box(S)` は「`S` に含まれない最初の rank `g` があれば `{0, ..., g}`、なければ全体」として計算します。最後に interval union を `box_power(bot(), n)` とその否定のブール結合に戻します。

`pytest`: 未実行。リポジトリ本体と `prove_gl` がこの環境にないため、passed 件数は申告しません。

[1]: https://hrcak.srce.hr/file/123527?utm_source=chatgpt.com "A note on normal forms for the closed fragment of system IL"
[2]: https://philosophy.mit.edu/boolos/?utm_source=chatgpt.com "George Boolos, 1940-1996"
[3]: https://math.berkeley.edu/~buehler/The%20Logic%20of%20Provability.pdf?utm_source=chatgpt.com "The Logic of Provability"
