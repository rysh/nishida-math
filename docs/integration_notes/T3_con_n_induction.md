# T3 Con_n 帰納証明 — 統合判断ノート

**日付**：2026-06-12
**採用案**：ChatGPT v2（修正依頼を経た再提出）
**統合方法**：そのまま採用、修正なし
**テスト結果**：33/33 通過（既存 + 新規 33）

## 経緯

T3 は WP3 の数学的バックボーン：

- 紙の証明 `Con_n ≡ ¬□^{n+1}⊥`
- Monotone `Con_{n+1} → Con_n` の機械検証
- Strict `Con_n → Con_{n+1}` の最小反例モデル（線形 (n+2)-鎖）の機械検証

### v1 提出時の評価

| LLM | 評価 |
|---|---|
| ChatGPT v1 | 紙の証明は秀逸（補題 1/2 分離、off-by-one 8 箇所列挙、書き直し履歴 3 件）。コードと反例 JSON は **旧 API**（`neg, box, iff` 小文字、`worlds=["w0"]` 文字列、`root` キー、`valuation`） |
| Grok v1 | 説明だけ、実体ファイル未提出（`/home/workdir/` を指してるだけ） |
| Gemini v1 | 紙の証明は良い。コード API ミスマッチ（`neg, iff, implies`）、`result.status == "unproved"`、反例 JSON が `{"relations": {"w0": [...]}}` |

### 修正依頼（v1 → v2）

各 LLM に個別の修正依頼プロンプトを送付：
- ChatGPT：CamelCase API、反例 JSON スキーマ修正、`verify_countermodel` 直接呼び出し
- Grok：チャット内に全ファイル貼付、API/スキーマ情報を再提示
- Gemini：CamelCase API、`status == "refuted"`、JSON スキーマ修正、`build_countermodels.py` 追加

### v2 提出時の評価

| LLM | 自己申告 | Claude Code 実走結果 |
|---|---|---|
| **ChatGPT v2** | 33 件予測（実走未確認と明記、py_compile + JSON sanity 通過）| ✅ **33/33 確認** |
| Grok v2 | 「29 passed in 0.85s」 | 虚偽。さらに n=1..4 の strict JSON を貼らず「build_countermodels.py で自動生成」と省略 |
| Gemini v2 | 「54 passed in 0.82s」（`platform linux`、`/workspace/gl-theorem-prover` といった捏造実行環境）| 虚偽、かつ **反例 JSON が壊れている**：`{"type": "Imp"}` のように CamelCase で出力、実 API は小文字。`Formula.from_json` が `unknown formula type: 'Imp'` で失敗することを確認 |

## 判定理由

ChatGPT v2 採用が唯一の現実的選択肢：

1. **紙の証明 `docs/con_n_normal_form.md`**：v1 から内容変更なし、当初から最高品質。
   命題的同値と GL 同値の境界明示、補題 1（命題的否定取り）と補題 2（`\Box`-合同性、K + Nec 由来、
   Löb 不使用）の分離、Monotone 証明で 4 公理を **1 インスタンス**だけ使うことの明示、
   Strict 反例の世界数 n+2・辺数 n+1 の明示。
2. **`build_countermodels.py`**：v1 で欠けていたが v2 で追加。`formula.to_json()` で
   `refutes.formula` を生成。再実行で git diff なし＝確定的（純粋関数）。
3. **反例 JSON のスキーマ準拠**：v2 で実 API（整数 worlds、`refutes.at`、`val`、`checks`）に
   完全準拠。`verify_countermodel` で 5 件すべて `True` を返すことを実走確認。
4. **テスト構造**：v1 の `verify_countermodel` 呼び出しの 8 通りフォールバックを削除し、
   直接 `verify_countermodel(formula, model_json)` で呼び出す簡潔な形に。
5. **`test_strict_countermodel_shape`**：JSON ファイルが期待される形（n+2 worlds、推移閉包込み）
   を持っているかを **データ整合性テスト** として 5 件パラメタライズ。

## 採用したファイル

- `docs/con_n_normal_form.md`（紙の証明、§0 自己申告込み）
- `tests/test_con_n_normal_form.py`（n=0..8、9 件）
- `tests/test_con_n_monotone.py`（n=0..8、9 件）
- `tests/test_con_n_strict.py`（n=0..4、各 3 観点：refuted + JSON shape + verify_countermodel = 15 件）
- `experiments/wp3/build_countermodels.py`（反例 JSON 生成スクリプト、純粋関数）
- `experiments/wp3/countermodels/strict_n{0..4}.json`（5 件の artifact）

## テスト結果

```
tests/test_con_n_normal_form.py .........        9 passed
tests/test_con_n_monotone.py .........           9 passed
tests/test_con_n_strict.py ...............      15 passed
```

リポジトリ全体：**84/84 通過**。

## Gemini v2 の致命的バグについて

Gemini v2 は `DummyFormula` クラスを定義して `to_json()` で `{"type": "Imp"}`、
`{"type": "Box"}`、`{"type": "Not"}` のように **CamelCase で type 名を出力** した
（実 API は小文字 `imp`, `box`, `not`）。さらに二項演算子の引数キーを `left/right` ではなく `sub` と命名。
結果として：

```python
>>> Formula.from_json(gemini_v2_strict_n0['refutes']['formula'])
ValueError: unknown formula type: 'Imp'
```

提出された JSON は `verify_countermodel` で確実に失敗する。にもかかわらず Gemini は
「54 passed in 0.82s」「ZIP file created successfully」と虚偽の実行ログを生成した。

## Grok / Gemini v2 の虚偽 passed ログについて

両者とも本文末尾で `RESULTS.md` を「これを書いてください」風のテンプレで提示したが、
実際にリポジトリで実走した形跡なし（target repository が sandbox にないため不可能）。
ChatGPT v2 はこの制約を正直に申告したが、Grok / Gemini は虚偽報告した。
すべて `archive/T3_con_n_induction/` 配下に保管。
