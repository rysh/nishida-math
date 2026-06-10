# 単独 LLM タスク（Single）ワークフロー

慎重度が低い、または LLM ごとの特性を活かしたい（Gemini の調査力、Grok の批判性など）
タスクは 1 LLM で十分。

## 手順

### 1. プロンプト組み立て

```
[1] _shared/preamble.md の全文
[2] single/S?_xxx.md の「## タスク」以降の全文
```

`_shared/triangulate_output_format.md` は **貼らない**。

### 2. 投入

各タスクで推奨 LLM が指定されている。それに従う：

- **S1 LP/古典評価器**：ChatGPT GPT-5 or o3（コード生成）
- **S2 letterless 正規形**：ChatGPT GPT-5（コード生成 + KAT 多め）
- **S3 Lean/Isabelle 調査**：Gemini Deep Research
- **S4 参考文献チェック**：Gemini 2.5 Pro（A は Deep Research）
- **S5 E-A3 敵対的レビュー**：Grok 4
- **S6 禁止表現スクリーナ**：ChatGPT GPT-5 or Grok 4

### 3. 出力受領

```
incoming/<task_id>/<llm>.md
```

### 4. Claude Code が受領 → 検証

- コードタスクは KAT 走行
- 調査タスクは URL の実在確認・ライブラリ名のスペル確認
- レビュータスクは §7 禁止表現自己点検の確認

### 5. アーカイブ

採用後は `archive/<task_id>/` へ。

## 単独で十分な根拠

- **S1 LP/古典**：真理値表総当たり、間違える余地が小さい
- **S2 letterless 正規形**：KAT を多めに用意すれば誤りは即発見できる
- **S3 / S4 調査**：URL 実在確認が真理判定の主役、LLM 並走では解決しない
- **S5 レビュー**：「批判が当たっているか」は Claude Code + 数学側で判定
- **S6 スクリーナ**：誤検出は実運用で調整できる

ただし **S2 letterless** はサイレント失敗リスクがあるので、結果が怪しければ
triangulate に格上げする可能性あり。
