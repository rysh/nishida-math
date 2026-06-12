v2 ZIP を作成しました。

[Download `S2_letterless_normal_form_v2.zip`](sandbox:/mnt/data/S2_letterless_normal_form_v2.zip)

内容：

```text
S2_letterless_normal_form_v2/
├── src/gl/letterless.py
├── tests/test_letterless_kats.py
├── tests/test_letterless_random.py
└── RESULTS.md
```

反映内容：

* `Formula` の固定 dataclass スキーマに直接合わせ、前回の汎用 view 層を削除。
* `letterless.py` 内では `gl.tableau` / `gl.kripke_search` を import しない構成を維持。
* `tests/test_letterless_kats.py` 冒頭に AST import 分離テストを追加。
* KAT は独立 prover による 2 段階検証構造を維持。
* `RESULTS.md` に dispatch KAT 表 6 行目の訂正ブロックを明記。

実走については、こちらの環境には統合対象リポジトリ本体がなく、`src/gl/formula.py`・`src/gl/tableau.py`・既存 26 テスト・`pyproject.toml` が存在しないため、統合状態での `X passed` は申告していません。`RESULTS.md` に、実行試行結果、失敗理由、期待される pytest item 数 `26 existing + 15 new = 41` を明記しています。
