修正版 v2 を作成しました。

* [T3_con_n_normal_form_v2.zip](sandbox:/mnt/data/T3_con_n_normal_form_v2.zip)
* [RESULTS.md](sandbox:/mnt/data/T3_con_n_normal_form_v2/RESULTS.md)
* [tests/test_con_n_normal_form.py](sandbox:/mnt/data/T3_con_n_normal_form_v2/tests/test_con_n_normal_form.py)
* [tests/test_con_n_monotone.py](sandbox:/mnt/data/T3_con_n_normal_form_v2/tests/test_con_n_monotone.py)
* [tests/test_con_n_strict.py](sandbox:/mnt/data/T3_con_n_normal_form_v2/tests/test_con_n_strict.py)
* [experiments/wp3/build_countermodels.py](sandbox:/mnt/data/T3_con_n_normal_form_v2/experiments/wp3/build_countermodels.py)
* [docs/con_n_normal_form.md](sandbox:/mnt/data/T3_con_n_normal_form_v2/docs/con_n_normal_form.md)

修正内容は以下です。

1. `gl.formula` import を CamelCase API に修正しました。

   * `Box`, `Not`, `Iff`, `Imp`, `box_power`
   * `neg`, `box`, `iff`, fallback 探索コードは削除

2. `test_con_n_strict.py` を指定の直接呼び出しに修正しました。

   * `from gl.countermodel_verifier import verify_countermodel`
   * `verify_countermodel(formula, model)` の bool 判定
   * `prove_gl(Imp(Con(n), Con(n + 1))).status == "refuted"` も追加

3. countermodel JSON を指定スキーマに修正しました。

   * `worlds`: 整数 list
   * `rel`: 整数ペア list
   * `val`: `{}`
   * `root` 削除
   * `valuation` 削除
   * `refutes.formula` 追加
   * `refutes.at = 0`
   * `checks.transitive / checks.irreflexive` 追加

4. `experiments/wp3/build_countermodels.py` を追加しました。

   * `strict_n0.json` through `strict_n4.json` を生成
   * `Imp(Con(n), Con(n + 1)).to_json()` で `refutes.formula` を出力
   * relation は推移閉包込みで `i < j`

5. `docs/con_n_normal_form.md` は紙の証明本文は維持し、v2 artifact と矛盾しないよう JSON schema 例と API 名だけ合わせました。

実走確認については、こちらの sandbox にはリポジトリ本体の `gl` パッケージが存在しないため、`uv run pytest -q` は collection 時点で `ModuleNotFoundError: No module named 'gl'` になります。これは `RESULTS.md` に正直に記録しています。こちらで実施できた確認は、Python 構文チェックと JSON / relation / refutation sanity check で、これらは通っています。
