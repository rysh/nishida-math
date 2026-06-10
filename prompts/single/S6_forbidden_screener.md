# S6: §7 禁止表現スクリーナ（WP5 補助）

> 🎯 これは **単独 LLM タスク**（推奨：ChatGPT GPT-5 or Grok 4）。
>
> **前置き**：`_shared/preamble.md` を冒頭に貼る。

---

## タスク

指示書 §7 の **禁止表現** を CI で自動スクリーニングする仕組みを設計。

禁止：
1. シミュレーションが「哲学的テーゼを **証明する**」
2. 「西田が Gödel を **予見した**」（歴史的主張として）
3. 数学的内容に対する **新規性主張**
4. 因果消去主義的一般化

引用語法：既定は "consistent with / converges with / provides formal support for"。
"building on / following" は西田と本論文著者本人のみ。

## 仕様

### Layer 1：高速正規表現

- 危険語の存在検出（英語・日本語別）
- 過剰検出 OK、Layer 2 で絞る

### Layer 2：LLM 判定器

- Layer 1 ヒットの周辺 ±200 文字を切り出し
- 「禁止条項のどれに該当するか / 無害か」を JSON で返す
- 出力：`{"hit": bool, "violation_id": 1|2|3|4|null, "reason": str, "suggested_fix": str|null}`
- 4 条項それぞれの few-shot 例（陽性 2 / 陰性 2）込み

### CI 統合

- GitHub Actions `screen-forbidden.yml`
- `*.md` 全スキャン
- Layer 1 ヒット → Layer 2 呼び出し → violation で PR fail + 該当行コメント

### False positive 抑制

- 引用ブロック（```…```）、コードコメント、参考文献リストは除外
- 「禁止される」「avoid X」のような **言及自体** は陰性
- 指示書・本ファイル自身は CI 対象除外（pathspec）

### 提出物

1. `screener/forbidden_patterns.yaml`
2. `screener/judge_prompt.md`
3. `screener/cli.py`（`uv run screener path/`）
4. `.github/workflows/screen-forbidden.yml`
5. `screener/tests/fixtures/`（陽性 5 / 陰性 5）

## 注意

- API キーは GitHub Secrets
- Layer 2 は Layer 1 ヒット時のみ
- 判定ログを集めて改善する仕組み

Claude Code は結果を `screener/` 配下に置き WP5 統合時に CI 組み込み。
