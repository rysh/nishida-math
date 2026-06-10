# 3 LLM 並走（Triangulate）ワークフロー

このプロジェクトの慎重度高タスクは、ChatGPT / Grok / Gemini に **独立に同じ問題** を
投げ、Claude Code が差分統合する。

## 手順

### 0. タスク選定

- `triangulate/T{1,2,3,...}_*.md` のいずれかを開く
- 慎重度高（off-by-one や論理ニュアンスのある実装）であることを再確認

### 1. プロンプト組み立て

各 LLM 用に同じ 3 ブロックを連結：

```
[1] _shared/preamble.md の全文
[2] _shared/triangulate_output_format.md の全文
[3] triangulate/T?_xxx.md の「## タスク」以降の全文
```

3 LLM すべて **同一のプロンプト** を投げる（バイアスを避ける）。

### 2. 投入

各 LLM の Web UI または API：

- **ChatGPT**：GPT-5 または o3。コード生成主軸。
- **Grok**：Grok 4 最新。批判的レビューが鋭い。
- **Gemini**：2.5 Pro。長文整理が強い。Deep Research は調査タスク限定。

新規スレッドで投げる（過去文脈を引きずらないため）。

### 3. 出力受領

各 LLM の出力を以下に保存：

```
incoming/<task_id>/chatgpt.md
incoming/<task_id>/grok.md
incoming/<task_id>/gemini.md
```

`<task_id>` は `T1_gl_prover` のようにプロンプトファイル名と一致させる。

### 4. Claude Code に差分統合を依頼

以下のテンプレで依頼：

> `incoming/<task_id>/` の 3 案を読んで差分統合して。
> 1. 3 案の §0 自己申告を比較。誰がどこに不安と言っているか
> 2. §2 疑似コードを並べて構造差分を抽出
> 3. §3 Python 実装で意見の割れた箇所を抽出
> 4. 各 KAT を通せる部分を採用候補に
> 5. 最終実装は Claude Code が書く（採用候補をベースに）
> 6. KAT を実行して落ちたら、§5「自分のデバッグ手順」を参照して順に潰す

### 5. 検証

最終実装に対して：
- KAT pytest
- random battery
- 必要なら別タスクの triangulate 出力（例：T1 で T2 を検証）

### 6. アーカイブ

採用後、`incoming/<task_id>/` を `archive/<task_id>/` に移し、
`docs/integration_notes/<task_id>.md` に「3 案のどこを採ったか」を記録。

## 重要な原則

- **そのまま動くと思わない**：3 案ともコードを走らせる前に Claude Code が読む
- **多数決ではない**：2 案が同じ間違いをしていることは普通にある
- **KAT が真理**：3 案合意でも KAT が落ちたら 3 案とも間違い
- **自己申告を読む**：§0 で「ここが不安」と書いている LLM は実際にそこを間違えている確率が高い
