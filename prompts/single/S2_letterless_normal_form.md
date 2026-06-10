# S2: Letterless 正規形 reducer（WP3 補助）

> 🎯 これは **単独 LLM タスク**（推奨：ChatGPT GPT-5）。
> ただし **黙って違う式を返すリスク**があるため、KAT を多めに用意して検出する。
>
> **前置き**：`_shared/preamble.md` を冒頭に貼る。

---

## タスク

GL の **letterless fragment**（命題変数を含まない式の集合）の正規形 reducer を実装する。

### 定理（Boolos 1993, Letterless Normal Form Theorem）

すべての letterless 式は □ⁿ⊥（n ≥ 0；□⁰⊥ = ⊥）のブール結合に GL-同値。
正規形は **□^n⊥ の有限集合のブール組み合わせ** として一意に表現可能。

### 仕様

```python
def is_letterless(F: Formula) -> bool:
    """F に atom 型ノードが一切ないか"""

def letterless_normal_form(F: Formula) -> NormalForm:
    """letterless 式を正規形 NF に変換。
    NF は {□^n⊥ : n ∈ S} 上のブール式として表現。
    F が letterless でなければ ValueError。"""

def nf_equiv(F1: Formula, F2: Formula) -> bool:
    """両方 letterless として正規形比較で GL-同値判定"""
```

### KAT（多めに）

| 入力 | 期待される正規形（GL-同値） |
|---|---|
| `⊥` | `□^0⊥` |
| `¬⊥` | `⊤` |
| `□⊥` | `□^1⊥` |
| `□□⊥` | `□^2⊥` |
| `¬□⊥` | `¬□^1⊥`（≡ Con_0） |
| `¬□¬□⊥` | `¬□^2⊥`（≡ Con_1） |
| `□⊥ ∨ ¬□⊥` | `⊤` |
| `□⊥ ∧ ¬□⊥` | `⊥` |
| `□(□⊥→⊥)` | `□^1⊥`（Löb instance：□(□⊥→⊥) → □⊥ で吸収） |
| `□⊤` | `⊤`（□⊤ は GL で定理） |
| `¬□¬⊤` | `¬□⊥ ↔ Con_0` の言い換え |
| `□(□A→A)` for letterless A | `□A`（Löb スキーマ） |

各 KAT について、本リポジトリの T1 GL 証明器で
`GL ⊢ input ↔ expected_normal_form` を **必ず機械検証**。

### Random Battery

- letterless 式をモーダル深さ ≤ 4 でランダム 500 個
- 各々の正規形を計算 → T1 で同値検証
- 違反は hypothesis で最小化して報告

### 提出物

1. `src/gl/letterless.py`
2. `tests/test_letterless_kats.py`
3. `tests/test_letterless_random.py`

### よくあるバグ（事前警告）

- □⊤ を ⊤ に reduce 忘れ（GL ⊢ □⊤ の事実）
- Löb instance の吸収忘れ
- ブール結合の正規化（DNF 等）で構文一致を取ろうとして失敗
  → **構文一致ではなく GL-同値で判定** すること
- □^0⊥ と ⊥ の同一視忘れ

これらは KAT で全部潰せるので心配は要らないが、自分の実装でカバーしているか確認。
