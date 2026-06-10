# S4: 参考文献の正確性チェック & Boolos 1993 章要約

> 🎯 これは **単独 LLM タスク**（指定：Gemini 2.5 Pro。§A は Deep Research）。
>
> **前置き**：`_shared/preamble.md` を冒頭に貼る。

---

## タスク A：書誌情報チェック

指示書 §10 の文献：

```
Gödel (1931).
Turing, "Systems of Logic Based on Ordinals" (1939).
Feferman, "Transfinite Recursive Progressions of Axiomatic Theories," JSL 27 (1962).
Segerberg, An Essay in Classical Modal Logic (1971).
Solovay, "Provability Interpretations of Modal Logic," Israel J. Math. 25 (1976).
Smoryński, Self-Reference and Modal Logic (1985).
Boolos, The Logic of Provability (1993).
Priest, "The Logic of Paradox," JPL 8 (1979).
Asenjo, "A Calculus of Antinomies," NDJFL (1966).
Franzén, Gödel's Theorem: An Incomplete Guide to Its Use and Abuse (2005).
Paulson, Isabelle/HOL incompleteness formalization (2015).
```

各文献について：
1. 著者名の正確な綴り（ダイアクリティクス含む — Gödel, Smoryński, Asenjo）
2. 正確なタイトル
3. 出版年・巻号・ページ
4. **DOI または永続 URL**
5. 出版社
6. 訂正：「正：…」「誤：…」

成果物：
- `docs/references.bib`（BibTeX）
- `docs/references_check.md`（差分レポート）

## タスク B：Boolos 1993 関連章の要約

可能な範囲で（書籍へのアクセス前提に動かず、公開抜粋を活用）、
**Boolos, *The Logic of Provability* (1993)** から WP1/WP2 実装に直接関わる章を要約。

### B-1. 固定点定理の構成的証明（T2 用）

- 章・節番号と正式タイトル
- アルゴリズムの **疑似コード**
- 各 KAT（指示書 §2.2 表）の Boolos 本文での扱い

### B-2. Letterless 正規形定理（S2 用）

- 章・節番号
- 正規形定理の正確なステートメント
- reduction アルゴリズム疑似コード

### B-3. GL タブロー / Kripke 完全性（T1 用）

- 章・節番号
- finite model property の証明スケッチ
- 推移的・反射禁止フレームでの完全性

要約は **数式と疑似コード重視**、文学的解説は最小限。Boolos 本文を直接引用するときは
ページ番号を付ける。

## 出力形式

```
# References Audit

## A. 書誌情報チェック

## B-1. Boolos 1993: 固定点アルゴリズム

## B-2. Boolos 1993: Letterless 正規形

## B-3. Boolos 1993: GL 完全性

## 付録：references.bib

## 付録：CITATION.cff
```

## 重要

- 書籍に直接アクセスできない場合は「アクセス不可」と明記し、代替として論文版
  （Boolos の固定点定理に関する別論文、Boolos 1979 など）を提案
- Smoryński 1985 や Boolos 1979 のソースも併記
- 推測で書誌情報を補わない
- すべての URL は実在を確認

Claude Code は結果を `docs/references.bib`, `CITATION.cff`, `docs/boolos_summary.md` に配置する。
