# T3: Con_n の正規形 ≡ ¬□^{n+1}⊥ の帰納証明

> 🔁 これは **3 LLM 並走タスク**（triangulate）です。
> **off-by-one を必ずやるタスク**。数式の精密さ自体が成果物。
>
> **前置き**：
> 1. `_shared/preamble.md` を冒頭に貼る
> 2. `_shared/triangulate_output_format.md` を続けて貼る
> 3. 以下の本文を貼る

---

## タスク

指示書 §2.3 の主張：

> Con_0 := ¬□⊥
> Con_{n+1} := ¬□¬Con_n
>
> 定理：**Con_n ≡ ¬□^{n+1}⊥**

この帰納証明を **完全に厳密に** 書いてください。
紙の証明だけでなく、本リポジトリの T1 GL 証明器で **GL ⊢ Con_n ↔ ¬□^{n+1}⊥** を
n=0..8 で機械検証する pytest コードも添える。

### 要件

#### 1. 紙の証明（Markdown 数式 + 厳密に）

- **Base case** n=0：Con_0 = ¬□⊥ ≡ ¬□^{0+1}⊥ ＝ ¬□^1⊥（自明だが書く）
- **Step**：Con_n ≡ ¬□^{n+1}⊥ を仮定して Con_{n+1} ≡ ¬□^{n+2}⊥ を示す
  - Con_{n+1} = ¬□¬Con_n
  - 仮定で ¬Con_n ≡ □^{n+1}⊥（命題論理での否定取り）
  - よって Con_{n+1} ≡ ¬□(□^{n+1}⊥) ＝ ¬□^{n+2}⊥
  - 各 step で **何を使ったか** を厳密に（命題的同値、□-単調性、Löb は使うか否か）

「命題的同値」と「GL-同値」の **区別** をつけること。
¬Con_n と □^{n+1}⊥ の同値は **命題論理的** に Con_n ≡ ¬□^{n+1}⊥ から従う
（GL の □ 規則は使わない）。ここを混ぜると証明全体が曖昧になる。

#### 2. 機械検証用テストコード

```python
# tests/test_con_n_normal_form.py
import pytest
from gl.formula import bot, box, neg, iff
from gl.tableau import prove_gl

def Con(n):
    """Con_n の定義通り（再帰）"""
    if n == 0:
        return neg(box(bot()))
    return neg(box(neg(Con(n - 1))))

def box_n(F, k):
    """□^k F"""
    for _ in range(k):
        F = box(F)
    return F

@pytest.mark.parametrize("n", range(9))
def test_con_n_normal_form(n):
    """Con_n ≡ ¬□^{n+1}⊥"""
    lhs = Con(n)
    rhs = neg(box_n(bot(), n + 1))
    result = prove_gl(iff(lhs, rhs))
    assert result.status == "proved", \
        f"Con_{n} ≡ ¬□^{{{n+1}}}⊥ の同値が GL で証明できない: {result}"
```

#### 3. (Monotone) Con_{n+1} → Con_n の証明

- 正規形を使って： ¬□^{n+2}⊥ → ¬□^{n+1}⊥
- 対偶： □^{n+1}⊥ → □^{n+2}⊥
- これは □-単調性（A → □A は **言わない**、これは反射的になり GL では成立しない！）
  ではなく、**□A → □□A**（4 公理、GL では Löb から導出可能）の繰り返し適用
- 正確に書く：□^{n+1}⊥ ⊢ □^{n+2}⊥ は 4 公理の n+1 回適用ではなく **1 回適用 + 推移**

ここで LLM が **よく間違える**：
- 「□-単調性」と称して `A → B ⊢ □A → □B` の規則（GL では成立）と
  4 公理 `□A → □□A` を混同する
- 正しい導出を書くこと

#### 4. (Strict) Con_n → Con_{n+1} が **GL で証明不可** であることの反例モデル

- ¬(¬□^{n+2}⊥ → ¬□^{n+1}⊥) → ... ではなく、
- 反例の対象は `Con_n → Con_{n+1}` ＝ `¬□^{n+1}⊥ → ¬□^{n+2}⊥`
- 対偶： `□^{n+2}⊥ → □^{n+1}⊥` を反証
- 最小反例：**線形 (n+2)-鎖**（root から終端まで n+2 個の世界、推移閉包込み）
- root で `□^{n+2}⊥` 成立、`□^{n+1}⊥` 不成立

各 n=0..4 について、最小反例モデルを JSON で生成し、T1 の `verify_countermodel` で検証。

### 提出物

1. `docs/con_n_normal_form.md`（紙の証明、Markdown 数式）
2. `tests/test_con_n_normal_form.py`（n=0..8 機械検証）
3. `tests/test_con_n_monotone.py`（n=0..8）
4. `tests/test_con_n_strict.py`（n=0..4 + 反例モデル JSON）
5. `experiments/wp3/countermodels/strict_n{0..4}.json`（反例モデル artifact）

### このタスクで他案と差が出やすい論点（事前メモ）

- 帰納の step で命題論理的同値と GL 同値の境界をどこで引くか
- 4 公理（□A→□□A）の n 回適用の正確な書き下し（off-by-one の温床）
- 最小反例モデルの「線形 (n+2)-鎖」の世界数のカウント（n+1 個か n+2 個か n+3 個か？
  ここを LLM はよく外す）
- 反例モデル JSON の `rel` を推移閉包込みで書くか、生成側で閉包を取るか

これらは §7 で必ず触れてください。

### 特別な自己申告要請

§0 自己申告で：

- **off-by-one を自分が踏みうる箇所** を最低 5 つ列挙
- 上記紙の証明で **自分が一度書いた後に書き直した箇所** があれば、その before/after

を必ず書いてください。
