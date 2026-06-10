# T2: 固定点エンジン（Boolos 1993）

> 🔁 これは **3 LLM 並走タスク**（triangulate）です。
> このプロジェクトで **最も慎重に扱うべき箇所**。LLM がもっとも間違える。
>
> **前置き**：
> 1. `_shared/preamble.md` を冒頭に貼る
> 2. `_shared/triangulate_output_format.md` を続けて貼る
> 3. 以下の本文を貼る

---

## タスク

GL の **固定点定理**（de Jongh / Sambin, 1970s 中盤）の構成的アルゴリズムを
Python 3.12 で実装してください。

### 定理

任意のモーダル式 A(p) で **p が □ の下にのみ出現する**（modalized）とき、
GL ⊢ H ↔ A(H) を満たす H が A の他の変数のみから構成的に存在し、
GL-equivalence を除いて一意（Bernardi; de Jongh）。

実装参考：**Boolos, *The Logic of Provability* (1993)**（一次）；
Smoryński, *Self-Reference and Modal Logic* (1985)。

### 仕様

```python
def fixed_point(A: Formula, p: str) -> Formula:
    """A において p が □ 下にのみ出現するときに H を返す。
    H は p を含まず GL ⊢ H ↔ A[p := H]。
    modalized でなければ ValueError。"""

def is_modalized_in(A: Formula, p: str) -> bool:
    """p が A 内で □ の下にのみ出現するか（自由出現はない）"""
```

実装後、本リポジトリの GL 証明器（T1 出力）で **GL ⊢ H ↔ A[p := H] を必ず検証**。
検証が通らない出力は黙って捨てず例外。

### Known-Answer Tests（指示書 §2.2 表 — 必ず通す）

| 入力 A(p) | 期待 H |
|---|---|
| `¬□p` | `¬□⊥`（Gödel sentence ≡ Con） |
| `□p` | `⊤`（Henkin、Löb により inert） |
| `□p → q` | `□q → q`（Löb sentence） |
| `□¬p` | `□⊥`（Löb instance □(□⊥→⊥)→□⊥ で検証） |

KAT 1（H = ¬□⊥）の検証手順（テスト docstring に書く）：
- H ↔ ¬□H は □⊥ ↔ □¬□⊥ に帰着
- (→)：□⊥ から □ 単調性
- (←)：¬□⊥ ≡ (□⊥→⊥)、∴ □¬□⊥ ≡ □(□⊥→⊥)、Löb (A:=⊥) で □(□⊥→⊥)→□⊥

### Random Battery

- モーダル深さ ≤ 3、余分原子変数 ≤ 2、modalized A(p) を **≥ 200 個** 生成
- 各々 H を計算 → T1 証明器で `GL ⊢ H ↔ A[p := H]` を検証
- 通らないものは hypothesis の shrink 機構で最小化して報告

### 第 2 アルゴリズム（同一案内で別実装）

- Boolos アルゴリズムを 2 種類別ファイルで実装（簡易版でよい）
- 両出力 H₁, H₂ について `GL ⊢ H₁ ↔ H₂` を T1 で検証
- 一致しなければ片方／両方バグ

### 提出物

1. `src/gl/fixed_point.py`（主アルゴリズム）
2. `src/gl/fixed_point_alt.py`（代替実装）
3. `src/gl/modalized.py`（静的検査）
4. `tests/test_fixed_point_kats.py`
5. `tests/test_fixed_point_random.py`
6. `tests/test_fixed_point_uniqueness.py`

### このタスクで他案と差が出やすい論点（事前メモ）

- Boolos のアルゴリズムを **どの定式化で書くか**（substitution-based、Bernardi の
  uniqueness-経由、Smoryński の構成、Sambin の original のうちどれを基盤に？）
- modalized 性の静的検査の正確さ（束縛変数を持たない命題論理だが、出現位置の
  □-depth 追跡が必要）
- A(p) の前処理（DNF/NNF 正規化）を入れるか、入れるならその等価性を T1 で再検証
- 再帰の base case（A に p が出現しない場合）の扱い
- Löb の正方向 / 逆方向の適用判定

これらは §7 で必ず触れてください。

### 特別な自己申告要請

§0 自己申告で：

- **Boolos 1993 の該当章を本当に参照したか / 記憶を再構成したか / Web で参照したか**
- ハルシネーション可能性：Boolos のアルゴリズム原文と自分の実装の対応関係について
  どれくらい確信があるか

を必ず書いてください。
