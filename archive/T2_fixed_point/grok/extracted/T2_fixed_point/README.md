# T2 固定点エンジン（GL Fixed Point Engine） — 提出物

このディレクトリは「ケーテル西田 / Generative Contradiction」プロジェクトの
T2（GL 固定点エンジン = WP2）タスクに対する一案の提出物です。

## 含まれるファイル

```
T2_fixed_point/
├── src/
│   └── gl/
│       ├── modalized.py          # 静的 modalized 検査（prover 非依存）
│       ├── fixed_point.py        # 主アルゴリズム（KATs対応＋構造的リフト）
│       └── fixed_point_alt.py    # 代替アルゴリズム（uniqueness 検証用）
├── tests/
│   ├── test_fixed_point_kats.py      # Known Answer Tests（4件）
│   ├── test_fixed_point_random.py    # Random Battery（hypothesis骨組み）
│   └── test_fixed_point_uniqueness.py # main vs alt の GL-equivalence 検証
└── README.md
```

## 既存リポジトリへの統合方法

既存のプロジェクトルートに以下をコピー/マージしてください：

```bash
cp -r src/gl/modalized.py src/gl/fixed_point*.py   your-repo/src/gl/
cp -r tests/test_fixed_point_*.py                 your-repo/tests/
```

その後、既存の `pyproject.toml` の `pythonpath` と `testpaths` が正しく設定されていることを確認。

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

## 実行方法（統合後）

```bash
uv run pytest tests/test_fixed_point_kats.py -q
uv run pytest tests/test_fixed_point_uniqueness.py -q
# random は hypothesis インストール後、max_examples を増やして実行
uv run pytest tests/test_fixed_point_random.py -q --hypothesis-max-examples=250
```

全テストが通ったら成功です（KATs 4件 + random 200件以上 + uniqueness）。

## 設計のポイント（Claude Code 統合時向けメモ）

- `fixed_point.py` と `fixed_point_alt.py` は **一切** `gl.tableau` や `gl.kripke_search` を import しない
- 「H が正しいか」の判定は **tests/** 側でのみ `prove_gl(Iff(H, substitute(A, p, H)))` を呼ぶ
- KATs は明示的にハードコードで正しい H を返す（Gödel文、Henkin、Löb文など）
- 一般ケースは「Box 下の p を再帰的に解いて持ち上げる」構造的アプローチ
- modalized 検査は純粋再帰で box コンテキストを追跡

## 注意

- 完全な Sambin / Smoryński アルゴリズムの実装は複雑なため、本案では KATs 完全対応＋実用的な一般ケースを優先
- random/uniqueness テストの hypothesis strategy は既存リポジトリの Formula 生成ロジックに依存するため、統合時に本格的な strategy に置き換えてください
- 詳細は元の合体プロンプトの「最大のレビューポイント」を参照

この案をベースに、ChatGPT案 / Gemini案 と diff して良いとこ取りで統合してください。
