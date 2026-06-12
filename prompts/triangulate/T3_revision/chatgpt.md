# T3 修正依頼（ChatGPT 宛、同じスレッドで続けて貼る）

前回の T3 提出（`docs/con_n_normal_form.md` + 3 つの tests + 5 つの countermodel JSON）を
Claude Code がレビューしました。**紙の証明は秀逸**（補題分離、4 公理 1 インスタンスの明示、
off-by-one 8 箇所列挙、書き直し履歴）です。ただし **コードとアーティファクトが実 API と
噛み合っていません**。以下を修正してください。

## 1. Formula API の名前を CamelCase に修正

リポジトリの `src/gl/formula.py` が export しているコンストラクタは **すべて CamelCase**：

```
# 既存（あなたが使うべき）API：
from gl.formula import bot, atom, Not, And, Or, Imp, Iff, Box, box_power, con
```

`neg, box, iff, imp, implies, arrow` のような小文字版は **存在しません**。
あなたの `test_con_n_normal_form.py` などは `from gl.formula import bot, box, neg, iff` と
書いていますが、これは ImportError になります。

CamelCase に書き直してください：

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

`test_con_n_monotone.py` も `Imp(Con(n+1), Con(n))` を使うように直してください。

## 2. countermodel JSON のスキーマを修正

リポジトリの `verify_countermodel(formula, model)` が期待する model JSON のスキーマ：

```json
{
  "worlds": [0, 1, 2],
  "rel": [[0, 1], [0, 2], [1, 2]],
  "val": {},
  "refutes": {"formula": <formula JSON>, "at": 0},
  "checks": {"transitive": true, "irreflexive": true}
}
```

要点：

- **`worlds` は整数の list**。`"w0", "w1"` のような文字列ではありません
- **`rel` は整数ペアの list of list**。`[[0, 1], [0, 2], ...]`
- **`root` キーはない**。代わりに `refutes.at` が反証する world id
- **`valuation` ではなく `val`**
- `refutes` に formula JSON が必要（後述の通り、JSON 形式は `formula.to_json()` で得られます）

あなたの `strict_n0.json` の `"w0", "w1"` を `0, 1` に変える必要があります。
さらに `refutes.formula` フィールドを足してください。

具体的に：n=2 の例：

```json
{
  "worlds": [0, 1, 2, 3],
  "rel": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]],
  "val": {},
  "refutes": {
    "formula": <Imp(Con(2), Con(3)).to_json() の結果>,
    "at": 0
  },
  "checks": {"transitive": true, "irreflexive": true}
}
```

`refutes.formula` フィールドは `experiments/wp3/build_countermodels.py` の中で
`formula.to_json()` で生成してください。

## 3. `experiments/wp3/build_countermodels.py` を新規追加

dispatch の提出物 6 に書いた通り：

```
6. experiments/wp3/build_countermodels.py（artifact 生成スクリプト、純粋関数）
```

これが前回欠けています。strict_n*.json を生成する純粋関数を作って、スクリプトの
`__main__` ガードで実行できるようにしてください。Claude Code 側でも実走確認するため。

スクリプト内では `from gl.formula import box_power, bot, Not, Imp, Con`（必要なものだけ）と
し、`Imp(Con(n), Con(n+1)).to_json()` で formula JSON を得てください。

## 4. `verify_countermodel` の呼び出しを直接形に

前回 `test_con_n_strict.py` で `verify_countermodel` の置き場と引数順を 8 通り探索する
コードを書いていましたが、これは不要です。実際のシグネチャは：

```python
from gl.countermodel_verifier import verify_countermodel

result: bool = verify_countermodel(formula, model_json)  # True/False を返す
```

シンプルに書き直してください：

```python
@pytest.mark.parametrize("n", range(5))
def test_con_n_strict_countermodel(n: int):
    model_path = COUNTERMODEL_DIR / f"strict_n{n}.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    formula = Imp(Con(n), Con(n + 1))
    assert verify_countermodel(formula, model)
```

さらに、`prove_gl(Imp(Con(n), Con(n+1))).status == "refuted"` も別テストとして
パラメタライズして入れてください（dispatch §4 c）。

## 5. 紙の証明はそのままで OK

`docs/con_n_normal_form.md` は内容そのまま採用候補です。修正不要。

## 6. 実走確認（必須）

リポジトリトップで：

```bash
uv run pytest -q
```

既存テスト 26 件 + あなたの新規分が全部通ることを確認し、`X passed` を `RESULTS.md` に
報告してください。

## 提出形式

zip：

```
T3_con_n_normal_form_v2/
├── docs/con_n_normal_form.md            # そのまま
├── tests/test_con_n_normal_form.py      # CamelCase API に修正
├── tests/test_con_n_monotone.py         # 同上
├── tests/test_con_n_strict.py           # スキーマ修正 + シンプルな呼び出し
├── experiments/wp3/build_countermodels.py   # 新規追加
├── experiments/wp3/countermodels/strict_n0.json   # スキーマ修正
├── experiments/wp3/countermodels/strict_n1.json
├── experiments/wp3/countermodels/strict_n2.json
├── experiments/wp3/countermodels/strict_n3.json
├── experiments/wp3/countermodels/strict_n4.json
└── RESULTS.md                            # 実走結果 X passed
```

期限：可能な限り早めにお願いします。
