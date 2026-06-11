# S1 LP/古典評価器 — 統合判断ノート

**日付**：2026-06-11
**採用案**：ChatGPT（単独）
**統合方法**：そのまま採用、修正なし

## 経緯

S1 は単独 LLM タスク（指示書 §2.4 の LP + 古典命題論理評価器、E-B1/E-B2 実験）。
真理値表ベースで間違える余地が小さく、3 並走の価値が低いため ChatGPT 単独で投げた。

## 採用案の特徴

- `src/gl/formula.py` から `Formula` 型を import して **重複定義回避**
- `Box`（type="box"）を含む式は明示的に `ValueError` で拒否（指示書要件）
- LP 演算を `_LIT_ORDER` / `_ORDER_LIT` で順序写像する純粋関数
- bit-mask による entailment 計算（パフォーマンス考慮）
- §0 自己申告が冒頭、確信度 High、不安箇所 4 つ明示

## §0 自己申告の重要点

ChatGPT が以下を明示申告：

1. **E-B2 inertness の bounded suite 化**：指示書「任意の小 T と λ-free B」を有限化
   - 4 atoms、110 個の λ-free formulas、premise set size ≤ 2
   - base 81 valuations、full 243 valuations で違反ゼロ確認
   - これは proof ではなく executable check / illustration として明記
2. `And() / Or()` の空引数を `t / f` として扱った（gl.formula.And/Or の空対応未確認）
3. artifact JSON を summary（指定キーのみ）と `_details` に分離
4. MP/DS failure witness の最小性は主張せず、指定通り `v(A)=b, v(B)=f`

確認結果：(2) は問題なし — `Formula("and", args=())` の `to_json()` は `{"type":"and","args":[]}`、
GL 評価器の `_eval` で `all(...) == True`（古典の真）と一貫。LP も `min()` の reduce で同様。

## テスト結果

```
tests/test_classical.py ....   (4 tests)
tests/test_gl_kats.py ..........   (14 tests, 既存)
tests/test_gl_random.py .   (1 test, 既存)
tests/test_lp.py .......   (7 tests)
```

**26/26 passed**。実験スクリプトも実行確認、artifacts と一致。

## 採用したファイル

- `src/lp/evaluator.py`、`src/lp/entailment.py`、`src/lp/__init__.py`
- `src/classical/evaluator.py`、`src/classical/entailment.py`、`src/classical/__init__.py`
- `experiments/wp4/e_b1_classical_explosion.py`、`experiments/wp4/e_b2_lp_quarantine.py`
- `experiments/wp4/artifacts/*.json`（再現可能だが、レビュー利便性のためコミット）
- `tests/test_lp.py`、`tests/test_classical.py`

## pyproject.toml の変更

- `name` を `generative-contradiction-gl-prover` → `generative-contradiction`
- `description` を LP/classical/hierarchy 全体を含むものに更新
- `[tool.hatch.build.targets.wheel]` の `packages` に `src/lp`, `src/classical` を追加

## 未検証（将来の課題）

- inertness の有界性：4 atoms / premise ≤ 2 を超えた場合の挙動（一般的には LP の保存性定理
  により無限大でも保持されるべきだが、機械的な確認は有界の範囲のみ）
- `evaluate_lp` の `atom` 分岐で `value not in DESIGNATED and value != "f"` チェックがあるが、
  これは `value not in {"t","b","f"}` と等価。意図的な書き方
