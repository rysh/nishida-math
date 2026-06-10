# S1: LP / 古典命題論理の評価器（WP4）

> 🎯 これは **単独 LLM タスク**（推奨：ChatGPT GPT-5 or o3）。
> 真理値表ベースで間違える余地が小さく、3 並走の価値は低い。
>
> **前置き**：`_shared/preamble.md` を冒頭に貼る。

---

## タスク

指示書 §2.4 の LP（Priest's Logic of Paradox）と古典命題論理の評価器を
Python 3.12 で実装し、指示書 E-B1, E-B2 の実験を走らせる。

### LP の定義（指示書 §2.4）

- 値：{t, b, f}、順序 f < b < t
- 指定値（designated）：{t, b}
- ¬(t)=f, ¬(b)=b, ¬(f)=t
- ∧ = min, ∨ = max
- A → B := ¬A ∨ B
- Γ ⊨_LP φ ⇔ Γ をすべて指定する任意 valuation が φ も指定

### 古典命題論理

- LP の値 {t, f} 制限版（同じ機械）
- 比較のため同じインターフェイスで実装

### 仕様

```python
def evaluate_lp(formula: Formula, valuation: dict[str, Lit]) -> Lit:
    """Lit ∈ {'t', 'b', 'f'}。formula に □ が含まれていたら ValueError"""

def entails_lp(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool:
    """3^|atoms| 通り総当たり"""

def evaluate_classical(formula: Formula, valuation: dict[str, bool]) -> bool: ...
def entails_classical(premises: list[Formula], conclusion: Formula, atoms: list[str]) -> bool: ...
```

### E-B1 古典爆発展示

- λ ↔ ¬λ は古典で充足不可能 → 列挙 artifact
- 任意 B について λ↔¬λ ⊨_cl B（vacuous）の確認
- 出力 JSON：`{"satisfiable": false, "vacuous_explosion": true, "enumeration_size": int}`

### E-B2 LP quarantine 展示

- 充足性：v(λ)=b で λ↔¬λ が指定値 → valuation artifact
- **保存性（inertness）補題**：λ-free B について
  `T, λ∧¬λ ⊨_LP B ⇔ T ⊨_LP B`
  - 原子変数 ≤ 4（3^4 = 81 valuation、総当たり）
  - 任意の小 T と λ-free B で双方向確認
- **MP 失敗**：A, A→B ⊭_LP B、witness valuation を出力（v(A)=b, v(B)=f）
- **DS 失敗**：A∨B, ¬A ⊭_LP B、同様
- 出力 JSON：`{"satisfiable": true, "inert": true, "mp_failure": valuation, "ds_failure": valuation}`

### KAT

- 古典：λ↔¬λ が 2 valuation すべてで f
- LP：v(λ)=b で λ↔¬λ の値が b（指定）
- inertness：λ-free 言語 4 atoms 完全列挙で違反ゼロ

### 提出物

1. `src/lp/evaluator.py`
2. `src/lp/entailment.py`
3. `src/classical/evaluator.py`
4. `src/classical/entailment.py`
5. `experiments/wp4/e_b1_classical_explosion.py`
6. `experiments/wp4/e_b2_lp_quarantine.py`
7. `experiments/wp4/artifacts/`（出力 JSON）
8. `tests/test_lp.py`、`tests/test_classical.py`

### 注意

- formula 型は GL と共通（`shared_preamble.md` JSON スキーマ）。
  □ を含む式は LP/古典では拒否
- 純粋関数中心
