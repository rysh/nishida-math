```markdown
_shared/preamble.md

```

```markdown
_shared/triangulate_output_format.md

```

GL（Gödel-Löb）論理における証明可能性述語の反復的無矛盾性 $Con_n$ の正規形に関する帰納証明および機械検証の実装ですね。ご指摘の通り、このタスクはインデックスの off-by-one エラーや、命題論理的同値と GL-同値の混同、そして 4 公理の正確な適用が成否を分ける非常にデリケートな領域です。

厳密さと正確性を最優先に、完全な証明とコード、そして反例モデルを構築します。

---

## §0 自己申告（Self-Declaration）

### ⚠️ off-by-one を踏みうる危険箇所（5選）

1. **$Con_n$ と $\Box^k\bot$ のインデックスのズレ**: 定理 $Con_n \equiv \neg\Box^{n+1}\bot$ において、左辺が $n$ のとき右辺の $\Box$ の段数は $n+1$ になります。ここを $n$ 段と錯覚すると致命的です。
2. **反例モデル（線形鎖）の世界数**: $\Box^{n+2}\bot \to \Box^{n+1}\bot$ を反証する最小反例モデルは「線形 $(n+2)$-鎖」ですが、これに必要な世界数は（root を含めて）正確に $n+2$ 個です。深さが $n+1$ の木になるため、$n+1$ 個や $n+3$ 個と間違えやすいポイントです。
3. **帰納法ステップでの $\Box$ 重ね合わせ**: $\Box(\Box^{n+1}\bot)$ を $\Box^{n+2}\bot$ にまとめる際、添字の加算を誤るリスク。
4. **反例モデル生成時の range( ) の境界**: `for j in range(i+1, n+2)` とするべきところを `range(i+1, n+1)` とし、終端の世界への推移的関係を落としてしまうリスク。
5. **テストコード `box_n(F, k)` のループ回数**: `for _ in range(k)` において $k=n+1$ を渡すか $n$ を渡すかで $\Box$ のネスト数が1つズレるリスク。

### 📝 執筆中の自己修正（Before/After）

* **Before**: $Con_{n+1} \to Con_n$ の証明において、「$\Box A \to \Box\Box A$ を $A=\bot$ から始めて $n+1$ 回適用する」という筋道を立てかけました。
* **After**: 「$A = \Box^n\bot$ と置くことで、4 公理の **1回の適用** ($\Box(\Box^n\bot) \to \Box\Box(\Box^n\bot)$) と推移律だけで直接 $\Box^{n+1}\bot \to \Box^{n+2}\bot$ が導ける」と気づき、証明をより簡潔かつ厳密な形（指示書の要求通り）に書き直しました。

---

## §1 紙の証明（docs/con_n_normal_form.md）

以下が、GL における $Con_n \equiv \neg\Box^{n+1}\bot$ の完全な帰納証明です。

```markdown
# 定理: GL ⊢ Con_n ↔ ¬□^{n+1}⊥

## 定義
* $Con_0 := \neg\Box\bot$
* $Con_{n+1} := \neg\Box\neg Con_n$
* $\Box^0 A := A$
* $\Box^{k+1} A := \Box(\Box^k A)$

## 証明（$n$ に関する数学的帰納法）

### Base case ($n=0$)
定義より $Con_0 = \neg\Box\bot$ である。
一方、右辺は $\neg\Box^{0+1}\bot = \neg\Box^1\bot = \neg\Box\bot$ である。
両辺は構文的に全く同一の論理式であるため、自明に $\vdash_{GL} Con_0 \leftrightarrow \neg\Box^{1}\bot$ が成立する。

### Inductive step
ある $n \ge 0$ について、以下が GL で証明可能であると仮定する（帰納法の仮定、IH）。
$\vdash_{GL} Con_n \leftrightarrow \neg\Box^{n+1}\bot$

次に $n+1$ のケース、すなわち $\vdash_{GL} Con_{n+1} \leftrightarrow \neg\Box^{n+2}\bot$ を示す。

1. $Con_{n+1} = \neg\Box\neg Con_n$ （$Con$ の定義）
2. $\vdash_{GL} \neg Con_n \leftrightarrow \Box^{n+1}\bot$
   * (理由) 帰納法の仮定 (IH) に対し、命題論理の定理 $(P \leftrightarrow \neg Q) \to (\neg P \leftrightarrow Q)$ を適用した（**命題的同値**）。ここでは GL 固有の推論規則は一切用いていない。
3. $\vdash_{GL} \Box(\neg Con_n) \leftrightarrow \Box(\Box^{n+1}\bot)$
   * (理由) GL の合同性（Congruence）による。2 の結果に対して Necessitation 規則 ($A \Rightarrow \Box A$) と分配公理 K ($\Box(A \to B) \to (\Box A \to \Box B)$) を適用し、同値性を $\Box$ の内部に持ち込んだ（**GL-同値**）。Löb の公理は不要である。
4. $\Box(\Box^{n+1}\bot) \equiv \Box^{n+2}\bot$ （$\Box^k$ の定義）
5. $\vdash_{GL} \Box(\neg Con_n) \leftrightarrow \Box^{n+2}\bot$
   * (理由) 3 と 4 より。
6. $\vdash_{GL} \neg\Box(\neg Con_n) \leftrightarrow \neg\Box^{n+2}\bot$
   * (理由) 5 に対し、命題論理の定理 $(P \leftrightarrow Q) \to (\neg P \leftrightarrow \neg Q)$ を適用（**命題的同値**）。
7. $\vdash_{GL} Con_{n+1} \leftrightarrow \neg\Box^{n+2}\bot$
   * (理由) 6 の左辺を 1 の定義で置き換えた。

以上より、すべての $n \ge 0$ について $\vdash_{GL} Con_n \leftrightarrow \neg\Box^{n+1}\bot$ が示された。（証明終）

```

---

## §2 機械検証用テストコード（正規形）

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

---

## §3 $Con_{n+1} \to Con_n$ (Monotone) の証明とテスト

### 紙の証明

**定理**: $\vdash_{GL} Con_{n+1} \to Con_n$
**証明**:
正規形を用いると、示すべき命題は $\neg\Box^{n+2}\bot \to \neg\Box^{n+1}\bot$ である。
対偶をとると、$\Box^{n+1}\bot \to \Box^{n+2}\bot$ を示せばよい。

ここで、GL論理の定理である **4 公理（推移性）**: $\vdash_{GL} \Box A \to \Box\Box A$ を用いる。
この公理において、論理式 $A$ に $\Box^n\bot$ を代入する（**1回の適用**）。
$\vdash_{GL} \Box(\Box^n\bot) \to \Box\Box(\Box^n\bot)$

左辺と右辺の $\Box$ をそれぞれまとめると、
$\vdash_{GL} \Box^{n+1}\bot \to \Box^{n+2}\bot$
が得られる。この対偶をとることで命題論理的に $\neg\Box^{n+2}\bot \to \neg\Box^{n+1}\bot$、すなわち $Con_{n+1} \to Con_n$ が証明される。（証明終）

### テストコード

```python
# tests/test_con_n_monotone.py
import pytest
from gl.formula import bot, box, neg, implies
from gl.tableau import prove_gl
from test_con_n_normal_form import Con

@pytest.mark.parametrize("n", range(9))
def test_con_n_monotone(n):
    """Con_{n+1} → Con_n"""
    # Con_{n+1} -> Con_n が証明可能かテスト
    formula = implies(Con(n + 1), Con(n))
    result = prove_gl(formula)
    assert result.status == "proved", \
        f"Con_{n+1} → Con_n が GL で証明できない: {result}"

```

---

## §4 $Con_n \to Con_{n+1}$ (Strict) の反証テストと反例モデル

$Con_n \to Con_{n+1}$ は GL で証明不可能です。これを反証するには、対偶である $\Box^{n+2}\bot \to \Box^{n+1}\bot$ が成立しないクリプキモデル（最小反例）を構築します。

最小反例は、要素数 $n+2$ 個の推移閉包された線形鎖（Linear $(n+2)$-chain）です。

### テストコードとモデル検証

```python
# tests/test_con_n_strict.py
import json
import pytest
from pathlib import Path
from gl.formula import bot, box, neg, implies
from gl.tableau import prove_gl, verify_countermodel
from test_con_n_normal_form import box_n, Con

@pytest.mark.parametrize("n", range(5))
def test_con_n_strict(n):
    """Con_n → Con_{n+1} は証明不可であり、反例モデルで棄却される"""
    formula = implies(Con(n), Con(n + 1))
    result = prove_gl(formula)
    
    # 1. 証明不可であることを確認
    assert result.status == "unproved", \
        f"Con_{n} → Con_{n+1} が誤って証明された: {result}"
    
    # 2. 事前生成した反例モデルの読み込みと検証
    model_path = Path(f"experiments/wp3/countermodels/strict_n{n}.json")
    with open(model_path, "r") as f:
        model = json.load(f)
    
    # モデルのroot (w0) において、式が False になることを検証
    is_valid_in_model = verify_countermodel(formula, model, root="w0")
    assert is_valid_in_model is False, \
        f"反例モデル strict_n{n}.json で式が反証されなかった"

def generate_strict_countermodels():
    """反例モデル (n+2)-chain を生成するスクリプト"""
    out_dir = Path("experiments/wp3/countermodels")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for n in range(5):
        # n+2 個の世界を持つ線形鎖（推移閉包込み）
        num_worlds = n + 2
        worlds = [f"w{i}" for i in range(num_worlds)]
        
        # GL は推移的であるため、推移閉包を明示的に構築する
        relations = {
            f"w{i}": [f"w{j}" for j in range(i + 1, num_worlds)]
            for i in range(num_worlds)
        }
        
        model = {
            "worlds": worlds,
            "relations": relations,
            "valuation": {}  # bot は常に false なので空でよい
        }
        
        with open(out_dir / f"strict_n{n}.json", "w") as f:
            json.dump(model, f, indent=2)

if __name__ == "__main__":
    generate_strict_countermodels()

```

### 生成される JSON アーティファクトの例 ($n=2$ の場合)

`experiments/wp3/countermodels/strict_n2.json`
$n=2$ のとき、要素数は $n+2 = 4$ 個（$w_0, w_1, w_2, w_3$）です。

```json
{
  "worlds": [
    "w0",
    "w1",
    "w2",
    "w3"
  ],
  "relations": {
    "w0": ["w1", "w2", "w3"],
    "w1": ["w2", "w3"],
    "w2": ["w3"],
    "w3": []
  },
  "valuation": {}
}

```

---

## §5 提出ファイル一覧 (Artifacts)

1. `docs/con_n_normal_form.md` （§1 の紙の証明）
2. `tests/test_con_n_normal_form.py`
3. `tests/test_con_n_monotone.py`
4. `tests/test_con_n_strict.py`
5. `experiments/wp3/countermodels/strict_n0.json` ~ `strict_n4.json`

---

## §7 差が出やすい論点の考察

LLM間での品質の差（Triangulation における比較ポイント）は以下の点に現れます。

* **境界線の厳密性 (命題的同値 vs GL同値)**
帰納ステップで「どこからどこまでが命題論理による同値変形で、どこがGLの推論規則（K公理とNecessitationの組み合わせ）か」を明記しているかどうかが重要です。GL特有の「同値性の $\Box$ 内部への伝搬 ($\vdash A \leftrightarrow B \Rightarrow \vdash \Box A \leftrightarrow \Box B$)」に正しく触れているかで理解度が問われます。
* **4 公理の適用回数 (Monotone証明)**
「$\Box$-単調性 ($A \to \Box A$) の反復」と勘違いしがちな部分ですが、GLにおける $A \to \Box A$ は非定理です。また、「$\Box\bot \to \Box\Box\bot$ から始めて4公理を $n+1$ 回適用する」という冗長な説明もありがちです。最適かつ厳密な証明は、**「$A = \Box^n\bot$ として4公理を1回だけ適用する」** アプローチです。
* **最小反例モデルの頂点数 (off-by-one の温床)**
$\Box^{n+2}\bot \to \Box^{n+1}\bot$ を反証するモデルは、「深さが $n+1$」の木、つまり**頂点数が $n+2$ 個**の線形鎖です。インデックスに釣られて $n+1$ 個の世界を作ってしまうと反証に失敗します。
* **推移閉包の明示**
GL の関係 $R$ は推移的であるため、線形鎖をJSON化する際、`w0` から `w1` だけでなく、`w2, w3...` へのエッジも全て明示的に張る（推移閉包をとる）必要があります。ここを $w_i \to w_{i+1}$ のみにすると、GLクリプキフレームの定義（推移的非反射的）を満たさなくなります。本実装では内包表記 `range(i + 1, num_worlds)` により完全にカバーしています。