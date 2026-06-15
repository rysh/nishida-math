# prompts/ — LLM 委譲用プロンプト集

このディレクトリは、本プロジェクトの実装を ChatGPT / Grok / Gemini に委譲するときの
プロンプト雛形と、その出力を Claude Code が統合するためのワークフローを置く。

## 大方針

> 「LLM の出す式はそのまま動くと思ってはいけない」
>
> よって：3 つの LLM に独立に案を出させ、Claude Code がいいとこ取りで統合して動かす。
> ただし常に 3 並走するわけではなく、**慎重度に応じて 1 or 3** を使い分ける。

## 構成

```
prompts/
├── README.md                           # このファイル
├── _shared/
│   ├── preamble.md                     # 全プロンプト冒頭の共通前置き
│   └── triangulate_output_format.md    # 3 並走時の出力フォーマット強制
├── _workflow/
│   ├── how_to_triangulate.md           # 3 並走の手順
│   └── how_to_single.md                # 単独 LLM タスクの手順
├── triangulate/                        # 🔴 慎重度高：3 LLM 並走必須
│   ├── T1_gl_prover.md
│   ├── T2_fixed_point.md
│   └── T3_con_n_induction.md
└── single/                             # 🟢 単独 LLM で十分
    ├── S1_lp_classical_evaluator.md
    ├── S2_letterless_normal_form.md
    ├── S3_lean_isabelle_survey.md
    ├── S4_references_audit.md
    ├── S5_e_a3_adversarial.md
    ├── S6_forbidden_screener.md
    ├── S7_wp6_lean_instantiation.md
    └── S8_wp6_lp_truth_predicate.md
```

## タスク一覧と推奨 LLM

### 🔴 Triangulate（3 LLM 並走）

| ID | タスク | なぜ 3 並走 |
|---|---|---|
| T1 | GL 証明器（タブロー + Kripke 探索） | LLM は S4 タブローと GL タブローを混同しがち |
| T2 | 固定点エンジン（Boolos 1993） | **最も間違える**。Löb 適用方向と modalized 条件のミス頻発 |
| T3 | Con_n ≡ ¬□^{n+1}⊥ の帰納証明 | off-by-one 必発、数式の精密さが成果物 |

### 🟢 Single（単独 LLM）

| ID | タスク | 推奨 LLM | 理由 |
|---|---|---|---|
| S1 | LP / 古典評価器 | ChatGPT | 真理値表総当たり、間違える余地が小 |
| S2 | letterless 正規形 reducer | ChatGPT | KAT 多めで検出可能 |
| S3 | Lean/Isabelle 調査 | Gemini Deep Research | URL 実在確認が主、Web 探索強み |
| S4 | 参考文献チェック | Gemini | 長文整理 + Deep Research |
| S5 | E-A3 敵対的レビュー | Grok | 批判の鋭さ |
| S6 | 禁止表現スクリーナ | ChatGPT or Grok | 実装単純、誤検出は調整可 |
| S7 | WP6 E-C2 Lean ステージ1強化 | ChatGPT or Gemini | 既存ライブラリのインスタンス化、環境構築の正確さが要 |
| S8 | WP6 E-C1 LP 透明真理述語 | ChatGPT | KAT 多めで検出可（サイレント失敗中リスク） |

## クイックスタート

### 3 並走タスクを 1 つ走らせるとき

```
1. prompts/_workflow/how_to_triangulate.md を読む
2. prompts/triangulate/T?_xxx.md を選ぶ
3. 各 LLM に以下を貼る：
   - _shared/preamble.md
   - _shared/triangulate_output_format.md
   - triangulate/T?_xxx.md の本文
4. 出力を incoming/T?_xxx/{chatgpt,grok,gemini}.md に保存
5. Claude Code に「incoming/T?_xxx を統合して」と依頼
```

### 単独タスクを 1 つ走らせるとき

```
1. prompts/_workflow/how_to_single.md を読む
2. prompts/single/S?_xxx.md を選ぶ
3. 推奨 LLM に以下を貼る：
   - _shared/preamble.md
   - single/S?_xxx.md の本文
4. 出力を incoming/S?_xxx/<llm>.md に保存
5. Claude Code に検証を依頼
```

## 着手推奨順

1. **S3 Lean/Isabelle 調査**（Gemini Deep Research）— WP6 着手判断の前提
2. **T1 GL 証明器**（3 並走）— 他すべてが依存する基盤
3. **T2 固定点エンジン**（3 並走）— T1 完成後すぐ
4. **T3 Con_n 帰納**（3 並走）— T1 完成後
5. **S1 LP/古典** — T1/T2 と並行可
6. **S2 letterless** — T1 完成後
7. **S4 参考文献** — いつでも
8. **S5 E-A3 レビュー** — T1/T2/T3 完成後（議論の前提が固まる）
9. **S6 スクリーナ** — WP5 統合時
10. **S7 / S8 WP6**（任意・オプション）— コア（WP1–5）完成後。本体の主張には不要、装甲増し。
    S7（Lean インスタンス化）は `docs/wp6_survey.md` 必読。S8（LP 真理述語）は独立に着手可

## 不変式（再掲）

- LLM 出力 → KAT を通すまで採用しない
- 3 案合意でも 3 案とも間違っている可能性を疑う
- 自己申告 §0 で「不安」と書かれた箇所は実際に間違っている率が高い
- 指示書 §7 禁止表現は全出力でチェック
