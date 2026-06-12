# T3 修正依頼（Gemini 宛、同じスレッドで続けて貼る）

前回の T3 提出を Claude Code がレビューしました。**紙の証明は正しく書けています**
（off-by-one 5 つ列挙、書き直し履歴、4 公理 1 インスタンスの明示、(n+2) 鎖の世界数の説明）。
ただし、コードと反例 JSON が **実 API と噛み合っていません**。以下を修正してください。

## 1. Formula API の名前を CamelCase に修正

リポジトリの `src/gl/formula.py` が export しているコンストラクタは **すべて CamelCase**：

```python
# 正しい API：
from gl.formula import bot, atom, Not, And, Or, Imp, Iff, Box, box_power, con
```

あなたが書いた `from gl.formula import neg, box, iff, implies` は **すべて存在しません**。
ImportError になります。

修正版：

```python
# tests/test_con_n_normal_form.py
import pytest
from gl.formula import bot, Box, Not, Iff, box_power
from gl.tableau import prove_gl

def Con(n: int):
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))

@pytest.mark.parametrize("n", range(9))
def test_con_n_normal_form(n: int):
    lhs = Con(n)
    rhs = Not(box_power(bot(), n + 1))
    result = prove_gl(Iff(lhs, rhs))
    assert result.status == "proved"
```

`test_con_n_monotone.py` も同様に `Imp(Con(n+1), Con(n))` を使うように。

## 2. `result.status` の値

あなたは `assert result.status == "unproved"` と書きましたが、**`"unproved"` という値はありません**。
正しい値は **`"refuted"`** です。

```python
@pytest.mark.parametrize("n", range(5))
def test_con_n_strict(n: int):
    formula = Imp(Con(n), Con(n + 1))
    result = prove_gl(formula)
    assert result.status == "refuted"   # ← "unproved" ではない
    assert result.countermodel is not None
```

## 3. countermodel JSON のスキーマを修正

あなたの形式：

```json
{
  "worlds": ["w0", "w1", "w2", "w3"],
  "relations": {
    "w0": ["w1", "w2", "w3"],
    ...
  },
  "valuation": {}
}
```

これは **実 API と完全に違います**。正しいスキーマ：

```json
{
  "worlds": [0, 1, 2, 3],
  "rel": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]],
  "val": {},
  "refutes": {"formula": <Imp(Con(n), Con(n+1)).to_json() の結果>, "at": 0},
  "checks": {"transitive": true, "irreflexive": true}
}
```

差分：

- `worlds` は **整数 list**（文字列ではない）
- `rel` は **整数ペアの list of list**（隣接リスト辞書ではない）
- `valuation` ではなく **`val`**
- `refutes` フィールドが必須（formula JSON と reference world id）
- `checks` フィールドが推奨

## 4. `verify_countermodel` の呼び出し

```python
from gl.countermodel_verifier import verify_countermodel

ok: bool = verify_countermodel(formula, model_json)
```

`root="w0"` のような引数は受け付けません。`refutes.at` を見ます。

```python
@pytest.mark.parametrize("n", range(5))
def test_con_n_strict_countermodel(n: int):
    model = json.loads(Path(f"experiments/wp3/countermodels/strict_n{n}.json").read_text())
    formula = Imp(Con(n), Con(n + 1))
    assert verify_countermodel(formula, model)
```

## 5. `experiments/wp3/build_countermodels.py` のスキーマ準拠版

あなたの `generate_strict_countermodels` 関数を、上記スキーマに合わせて書き直してください。
`formula.to_json()` を使って `refutes.formula` を埋めてください：

```python
# experiments/wp3/build_countermodels.py
import json
from pathlib import Path
from gl.formula import bot, Box, Not, Imp, box_power

def Con(n: int):
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))

def build_strict_countermodel(n: int) -> dict:
    num_worlds = n + 2
    worlds = list(range(num_worlds))
    rel = [[i, j] for i in range(num_worlds) for j in range(i + 1, num_worlds)]
    formula = Imp(Con(n), Con(n + 1))
    return {
        "worlds": worlds,
        "rel": rel,
        "val": {},
        "refutes": {"formula": formula.to_json(), "at": 0},
        "checks": {"transitive": True, "irreflexive": True},
    }

def main():
    out_dir = Path("experiments/wp3/countermodels")
    out_dir.mkdir(parents=True, exist_ok=True)
    for n in range(5):
        model = build_strict_countermodel(n)
        (out_dir / f"strict_n{n}.json").write_text(
            json.dumps(model, indent=2, ensure_ascii=False) + "\n"
        )

if __name__ == "__main__":
    main()
```

## 6. 紙の証明はそのままで OK

`docs/con_n_normal_form.md` の §1 の内容は採用候補です。修正不要。

## 7. 実走確認（必須）

リポジトリトップで：

```bash
uv run pytest -q
```

既存テスト 26 件 + あなたの新規分が全部通ることを確認し、`X passed` を `RESULTS.md` に報告してください。

## 提出形式

zip：

```
T3_con_n_normal_form_gemini_v2/
├── docs/con_n_normal_form.md            # そのまま
├── tests/test_con_n_normal_form.py      # CamelCase API
├── tests/test_con_n_monotone.py         # 同上
├── tests/test_con_n_strict.py           # スキーマ修正、status "refuted"
├── experiments/wp3/build_countermodels.py
├── experiments/wp3/countermodels/strict_n0.json
├── ... (n=1..4)
└── RESULTS.md                            # 実走結果 X passed
```

期限：可能な限り早めにお願いします。
