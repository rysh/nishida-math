# T3 修正依頼（Grok 宛、同じスレッドで続けて貼る）

前回の T3 提出は「`/home/workdir/artifacts/` に作成しました」とだけ書かれていて、
**実体ファイルが Claude Code に届いていません**。提出物 zip は空でした。

## やってほしいこと

すべてのファイルを **このチャット内に貼って** zip にまとめてください。
`/home/workdir/` の内容は Claude Code 側からアクセスできません。

## 提出物（dispatch 通り）

```
T3_con_n_normal_form_grok/
├── docs/con_n_normal_form.md             # 紙の証明、§0 自己申告（off-by-one 5 つ、書き直し履歴）付き
├── tests/test_con_n_normal_form.py       # n=0..8
├── tests/test_con_n_monotone.py          # n=0..8
├── tests/test_con_n_strict.py            # n=0..4 + 反例モデル検証
├── experiments/wp3/build_countermodels.py # 反例 JSON 生成スクリプト
├── experiments/wp3/countermodels/strict_n0.json
├── experiments/wp3/countermodels/strict_n1.json
├── experiments/wp3/countermodels/strict_n2.json
├── experiments/wp3/countermodels/strict_n3.json
├── experiments/wp3/countermodels/strict_n4.json
└── RESULTS.md                             # 実走結果 X passed
```

## API 情報（重要）

リポジトリの `src/gl/formula.py` が export しているコンストラクタは **すべて CamelCase**：

```python
from gl.formula import bot, atom, Not, And, Or, Imp, Iff, Box, box_power, con
```

`neg, box, iff, imp, implies, arrow` のような小文字版は **存在しません**。

GL 証明器：

```python
from gl.tableau import prove_gl
result: ProofResult = prove_gl(formula)
# result.status は "proved" または "refuted"
```

反例検証器：

```python
from gl.countermodel_verifier import verify_countermodel
ok: bool = verify_countermodel(formula, model_json)
```

countermodel JSON のスキーマ（整数 world ID）：

```json
{
  "worlds": [0, 1, 2],
  "rel": [[0, 1], [0, 2], [1, 2]],
  "val": {},
  "refutes": {"formula": <formula.to_json() の結果>, "at": 0},
  "checks": {"transitive": true, "irreflexive": true}
}
```

## 確認すべき数学的事実

- `Con_n ≡ ¬□^{n+1}⊥`（指数は **n+1**、n ではない）
- Monotone `Con_{n+1} → Con_n` は、対偶 `□^{n+1}⊥ → □^{n+2}⊥` を経由し、
  これは 4 公理 `□A → □□A` の `A := □^n⊥` への **1 インスタンス適用**で得られる（n+1 回の繰り返しではない）
- Strict `Con_n → Con_{n+1}` の最小反例は **線形 (n+2)-鎖**（world 数 n+2、推移閉包込みの完全順序）

## 実走確認

リポジトリトップで：

```bash
uv run pytest -q
```

既存テスト 26 件 + あなたの新規分が全部通ることを確認し、`X passed` を `RESULTS.md` に報告してください。

期限：可能な限り早めにお願いします。
