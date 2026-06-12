# S2 Letterless 正規形 reducer — 統合判断ノート

**日付**：2026-06-12
**採用案**：ChatGPT v2（修正依頼を経た再提出）
**統合方法**：そのまま採用、修正なし
**テスト結果**：15/15 通過（既存 + 新規 15）

## 経緯

S2 は単独 LLM タスク（指示書 §3 E-A2 補助、WP3 の足場）。GL の letterless fragment
（命題変数なし）の正規形 reducer：

> すべての letterless 式は `□^n⊥` (n ≥ 0; `□^0⊥ = ⊥`) のブール結合に GL-同値（Boolos 1993 LNF Theorem）。

### v1 提出時の評価

v1 は ChatGPT 単独提出（Gemini が S2 として申告したものも実装内容は同じく ChatGPT 由来と判明）。
特筆すべき仕事：**dispatch の KAT 表のバグを発見して訂正**：

> `Not(Box(Not(Box(bot()))))` の正規形は `Not(box_power(bot(), 1))` であり、`Not(box_power(bot(), 2))` ではない。
>
> 理由：`Not(Box(bot()))` は `Imp(Box(bot()), bot())` と命題論理的同値、ゆえに `Box(Not(Box(bot())))` は
> `Box(Imp(Box(bot()), bot()))` と GL-同値。Löb instance `□(□⊥→⊥) → □⊥` と自明な逆向き
> `□⊥ → □(□⊥→⊥)` により `□⊥ = box_power(bot(), 1)` に reduce。両辺の否定を取って正規形が決まる。

実装は interval/rank semantics（closed GL fragment の標準実装）。

v1 の問題：
- Formula 型への過剰な汎用性（`_view`, `_normal_kind`, aliases 辞書）— 確定スキーマには不要
- 実走未確認

### 修正依頼（v1 → v2）

- 汎用 view 層削除（確定スキーマ向けに直接書く）
- AST 分離テスト追加
- 実走確認 + KAT 訂正の数学的根拠を `RESULTS.md` に

### v2 提出時の評価

| 項目 | 状態 |
|---|---|
| 汎用 view 層削除 | ✅ 432 行 → 283 行に減少。`_mapping_view`, `_field`, `_normal_kind`, `_unary_child`, `_binary_children`, `_nary_children`, `_as_sequence`, aliases 辞書すべて削除 |
| AST 分離テスト | ✅ `test_letterless_does_not_import_provers` 追加 |
| 自己申告（実走未確認） | ✅ 正直に「sandbox に target repository なし、py_compile + temporary stub での smoke check のみ」 |
| 件数予測 | 41 件（既存 26 + 新規 15）→ 実走確認で一致 |
| KAT 訂正の数学的根拠 | ✅ Löb instance + 自明な逆向きを含む完全な証明文を RESULTS.md に明記 |

## 判定理由

S2 は単独タスクなので比較は実質「v1 vs v2」のみ。v2 がすべての改善点を満たし、
実走確認 15/15 通過。

特筆すべき仕事は **dispatch のバグ発見**。Claude Code が指示書側の誤りを LLM 経由で
発見・訂正するメタな結果になっており、これは triangulate ワークフローの想定外の良い副作用。
今後の dispatch 作成時にも参考になる。

## 採用したファイル

- `src/gl/letterless.py`（interval/rank semantics、確定スキーマ向け、prover 非依存）
- `tests/test_letterless_kats.py`（14 件：AST 分離 1 + 訂正版 KAT 10 + 拒否 + ランダム sanity 等）
- `tests/test_letterless_random.py`（hypothesis 500 例 × 1 test）

## テスト結果

```
tests/test_letterless_kats.py ..............    14 passed
tests/test_letterless_random.py .                1 passed (500 examples)
```

リポジトリ全体：**84/84 通過**。

## 指示書側の修正履歴（KAT 訂正）

S2 の発見を受けて、**将来の dispatch 作成時に KAT 表の以下の行に注意**：

旧（誤）：

```
| `Not(Box(Not(Box(bot()))))` | `Not(box_power(bot(), 2))`（≡ Con_1） |
```

正：

```
| `Not(Box(Not(Box(bot()))))` | `Not(box_power(bot(), 1))`（≡ Con_0） |
```

近接する別 KAT として `Not(box_power(bot(), 2))` が期待値になるのは：

```
| `Not(Box(Box(bot())))` | `Not(box_power(bot(), 2))`（≡ Con_1） |
```

実装側は S2 v2 が訂正済の期待値で 14 件すべて通過済み。
