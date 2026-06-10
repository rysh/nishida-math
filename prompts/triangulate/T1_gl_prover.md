# T1: GL 証明器の実装

> 🔁 これは **3 LLM 並走タスク**（triangulate）です。
> 同じ依頼を ChatGPT / Grok / Gemini に独立に投げ、Claude Code が差分統合します。
>
> **前置き**：
> 1. `_shared/preamble.md` を冒頭に貼る
> 2. `_shared/triangulate_output_format.md` を続けて貼る
> 3. 以下の本文を貼る

---

## タスク

Gödel–Löb 証明可能性論理 GL の **証明器** を Python 3.12 で実装してください。
**2 つの独立した方法** を実装し、相互チェック可能にします。

### 方法 A：GL タブロー法

- 古典 α/β 規則
- □ 規則は GL タブロー固有（S4 ではない）：
  - 各タブロー世界は **irreflexive**（自分を見ない）
  - **逆 well-founded** ＝ ループ検出による有限化
  - □A が成り立つ世界からの後続世界では A が成り立つ
  - Löb 規則の正しい扱い（□(□A→A) → □A の方向）
- 出力：閉じたタブローの JSON certificate、または開いた枝からの Kripke 反例モデル

### 方法 B：有限 Kripke モデル探索

- 推移的・反射禁止の有限フレーム上で総当たり
- 探索深さは入力式のモーダル深さで bound
- ¬φ を充足するモデルが存在するか
- 出力：反例モデル JSON か「証明可能」

### 仕様

```python
def prove_gl(formula: Formula) -> ProofResult:
    """status='proved' | 'refuted',
       certificate: TableauJSON | None,
       countermodel: KripkeJSON | None"""
```

両方法は同じ入力 / 出力契約。

### 独立な反例モデル検証器

反例モデルが (a) transitive (b) irreflexive (c) 与えられた式を root で反証 を
**証明器とは別経路** で確認する純粋関数を `verify_countermodel` として実装。

### Known-Answer Tests（必ず通す）

```
GL ⊢ □(□A → A) → □A          # Löb
GL ⊢ □A → □□A                 # 4 公理（導出可能）
GL ⊢ ¬□⊥ → ¬□¬□⊥             # 第二不完全性形
GL ⊢ Con_{n+1} → Con_n        # 単調性 (n=0..4)
GL ⊬ Con_n → Con_{n+1}        # 厳密性 (n=0..4) — 反例モデル必須
```

ただし **Con_n ≡ ¬□^{n+1}⊥**（off-by-one に注意。n+1 乗）。

n=0 の厳密性反例 KAT：線形 2 鎖 `x → t`、t 終端、推移的・反射禁止。
方法 B はこれを最小として返すべき。

### Random Battery

- モーダル深さ ≤ 3、原子変数 ≤ 3 をランダム 1000 個
- 両方法が完全に一致すること
- 同じ式が「証明可能 かつ 反証可能」になったら **即 fail**

### 提出物

1. `src/gl/formula.py`
2. `src/gl/tableau.py`（方法 A）
3. `src/gl/kripke_search.py`（方法 B）
4. `src/gl/countermodel_verifier.py`
5. `tests/test_gl_kats.py`
6. `tests/test_gl_random.py`
7. `pyproject.toml`（uv, Python 3.12）

### このタスクで他案と差が出やすい論点（事前メモ）

- ループ検出のシグネチャ定義（世界ラベルの取り方）
- Löb 規則をタブロー規則として直接書くか、4 公理を通じて間接的に得るか
- modal subformula property を効かせる場面の選択
- 反例モデル抽出時、開いた枝の世界をどう順序付けるか

これらは §7 で必ず触れてください。
