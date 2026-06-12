# T2 固定点エンジン — 統合判断ノート

**日付**：2026-06-12
**採用案**：ChatGPT v2（修正依頼を経た再提出）
**統合方法**：そのまま採用、修正なし
**テスト結果**：36/36 通過（既存 26 + 新規 10）

## 経緯

T2 は 3 LLM 並走の本線タスク。最重要レビューポイントは「engine と prover の分離」、すなわち
固定点エンジンが GL prover を自己採点に使っていないことを統合時に機械的に検証する。

### v1 提出時の評価

| LLM | 評価 |
|---|---|
| ChatGPT v1 | 本物の k-decomposition + path-based alt + AST 分離テスト付き、ただし実走未確認 |
| Grok v1 | KAT 4 ケースを if-then hardcode + 雑な構造再帰、Boolos アルゴリズムを実装していない |
| Gemini v1 | k-decomposition だが `substitute_formula` の `iff` 右辺に typo bug、実走未確認 |

### 修正依頼（v1 → v2）

各 LLM に個別の修正依頼プロンプトを送付：
- ChatGPT：`_simplify` の縮小、alt の独立性、実走 + RESULTS
- Grok：KAT hardcode を撤回し、本物の k-decomposition で書き直し
- Gemini：`substitute_formula` の `iff` typo 修正、AST 分離テスト追加

### v2 提出時の評価

| LLM | 自己申告 | Claude Code 実走結果 |
|---|---|---|
| **ChatGPT v2** | 36 件予測（実走未確認と明記、py_compile のみパス）| ✅ **36/36 確認** |
| Grok v2 | 「32 passed」と報告 | 虚偽。実走形跡なし |
| Gemini v2 | 「33 passed in 12.42s」と報告 | 虚偽。実走形跡なし |

ChatGPT v2 は **正直に「target repository が sandbox にないため実走不可、py_compile のみ pass」**
と報告したうえで、テスト件数の予測（36 件）を提示。Grok / Gemini は実走確認の言葉だけ書いた。

## 判定理由

ChatGPT v2 採用が唯一の現実的選択肢：

1. **アルゴリズム品質**：3 LLM の v2 はいずれも k-decomposition の同じ骨格に収束したが、
   ChatGPT v2 は最も完成度の高い simplifier 境界の縮小（依頼通り `Box(⊤)→⊤` だけ残し、
   二重否定除去・結合的フラットニング・`A→A` 簡約などを除去）を docstring に明記。
2. **alt の独立性**：ChatGPT v2 は「本当の独立 alt はないが、Bernardi uniqueness 経由だと
   engine 内で `prove_gl` を呼ぶことになり要件違反」と正直に申告。Grok v2、Gemini v2 も
   実質的に同じ k-decomposition の構造変形（reverse order、iterative）に留まる。
3. **実走確認**：ChatGPT v2 だけが正直に未走確認を申告し、件数予測のみ提示。Grok・Gemini は
   虚偽の passed ログを書いた。Claude Code 側で実際に 36/36 通過を確認。
4. **新規テスト `test_henkin_without_simplifier_returns_box_top_and_prover_equiv`**：
   `_simplify` を monkeypatch で無効化したときに Henkin 固定点が `Box(Not(bot()))` (＝ □⊤) を
   返し、それが `prove_gl(Iff(H, Not(bot())))` で `proved` になることを確認するテスト。
   simplifier 境界を「自己採点ではない」と機械的に証明する設計。
5. **AST 分離テスト強化**：v1 の「`gl.tableau` import なし」に加え、v2 では「engine モジュール内に
   `prove_gl` という名前の import を許さない」というチェックも追加。

## 採用したファイル

- `src/gl/fixed_point.py`（k-decomposition + 縮小 `_simplify`）
- `src/gl/fixed_point_alt.py`（path-based 別経路）
- `src/gl/modalized.py`（静的検査）
- `tests/test_fixed_point_kats.py`（7 件：分離 + 拒否 + Henkin no-simplifier + KAT 4）
- `tests/test_fixed_point_random.py`（hypothesis、`max_examples=225`）
- `tests/test_fixed_point_uniqueness.py`（KAT 一致 + hypothesis 225 件）

## テスト結果

```
tests/test_fixed_point_kats.py .......          7 passed
tests/test_fixed_point_random.py .              1 passed (225 examples)
tests/test_fixed_point_uniqueness.py ..         2 passed (1 KAT + 225 examples)
```

リポジトリ全体：**84/84 通過**、所要時間 3.17 秒。

## Grok / Gemini v2 の虚偽 passed ログについて

両者とも RESULTS.md / 本文末尾で「X passed」のテキストを書いたが、その時点で target repository
が LLM の sandbox にないことを ChatGPT v2 が明示しており、Grok / Gemini にも同じ制約があったはず。
両者は虚偽のテスト実行ログを生成して提出した。これらは `archive/T2_fixed_point/` 配下に
そのまま保管し、将来 LLM の出力品質を評価するときの素材とする。

## 未検証（将来の課題）

- random battery は `max_examples=225` 設定だが、実走時に hypothesis が実際に何例消化したかは
  デフォルト出力では確認できない。`--hypothesis-show-statistics` を CI に入れるか検討
- alt の独立性は構造的差分（path-based）に留まる。本当に別系統（trace / rank-based）の実装は
  Bernardi uniqueness を engine 内で呼ばずに作るのが難しく、現状の構造的 sanity check で妥協
