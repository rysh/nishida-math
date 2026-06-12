# T2 修正依頼（Grok 宛、同じスレッドで続けて貼る）

前回の T2 提出を Claude Code がレビューした結果、**根本的な書き直しが必要**です。
以下を読んで再提出してください。

## 1. 主な問題：fixed_point が KAT ハードコード＋雑な構造再帰になっている

あなたの `src/gl/fixed_point.py` は、KAT 4 ケースを `if A == Not(Box(atom(p)))` のように
**明示パターンマッチで返し**、それ以外は「Box の中身を再帰的に解いて持ち上げる」だけです。
これは **de Jongh / Sambin / Boolos のアルゴリズムを実装したものではありません**。

具体的に何が問題か：

- `A = Or(Box(Not(atom("p"))), Box(atom("p")))` のように **複数の outermost p-box** がある A について、
  あなたの再帰は両方とも独立に `Box(inner_H)` に置き換えますが、これは固定点になっていません。
  Boolos のアルゴリズムは k-decomposition：`A = B(x1, ..., xk)` の各 xi を一つだけ ⊤ に置き換えた
  Bi の固定点 Hi を再帰的に求め、最終的に `B(Box(D1(H1)), ..., Box(Dk(Hk)))` を返します。
- `A = Box(Box(atom("p")))` のような **入れ子 box** について、あなたの再帰は外側 box の中で
  `fixed_point(Box(atom("p")), "p") = Not(bot())` を計算し `Box(Not(bot()))` を返しますが、
  これは GL ⊢ □⊤ ≡ ⊤ で実は ⊤ と同値で、正しい固定点はもっと精緻に決まります。
- 「フォールバック」分岐 `return A` は **明らかに固定点になっていない**。p が含まれているのに
  そのまま返すのは fixed_point の方程式 H ↔ A[p:=H] を満たしません。

## 2. やってほしいこと

### A. Boolos の k-decomposition を本気で実装する

擬似コード：

```
fixed_point(A, p):
    if not is_modalized_in(A, p): raise ValueError
    A := simplify_constants(A)            # 定数畳み込みだけ。GL の同値変形はしない
    if p not in atoms(A): return A

    # outermost p-boxes をすべて placeholder に置き換え：
    # A = B(box(D1(p)), ..., box(Dk(p)))
    # B には x1,...,xk という fresh atom が入る
    B, placeholder_names, Ds = decompose_outermost_p_boxes(A, p)

    # 各 i について「i 番目だけ ⊤、他は元の box」に置き換えた式の固定点を再帰計算
    Hs = []
    for i in range(k):
        replacements = {}
        for j in range(k):
            replacements[placeholder_names[j]] = Not(bot()) if i==j else Box(Ds[j])
        Bi = B with placeholders replaced
        Hs.append(fixed_point(Bi, p))

    # 元の B に Box(Di[p:=Hi]) を埋める
    final = B with each placeholder_i replaced by Box(substitute(Di, p, Hs[i]))
    return final
```

KAT を if-else で先に当てるのは禁止です。**一般アルゴリズムが KAT も自然に通る** ことを示してください。

### B. engine と prover の分離は維持

`src/gl/fixed_point.py` は `gl.tableau` / `gl.kripke_search` を import しないこと（前回は守れていました、継続して守ってください）。

### C. 実走確認

リポジトリトップで：

```bash
uv run pytest -q
```

`prove_gl` は `from gl.tableau import prove_gl` で使えます。`ProofResult.status == "proved"|"refuted"`。
今度は **必ず実走して `X passed` を報告** してください。前回「`X passed` を取得できなかった」と書きましたが、
今回はリポジトリ全体（既存 26 件 + あなたの新規分）を実走させてください。

### D. random battery 200 件以上

dispatch の通り、modal_depth ≤ 3、余分原子 ≤ 2 の modalized A(p) を hypothesis で 200 件以上生成し、
各々 `prove_gl(Iff(H, substitute(A, p, H))).status == "proved"` を確認してください。
実装が k-decomposition で正しければ通るはずです。**通らないものがあれば** hypothesis の shrink で
最小化し、その A と返した H を `RESULTS.md` に列挙してください。

### E. 第 2 アルゴリズム

alt は dispatch では「簡易版でよい」と書きました。たとえば：

- 主実装が **再帰的 k-decomposition** なら、alt は **iterative version**（ループで k 回 placeholder を解消）
- あるいは **explicit placeholder fresh name** vs **path-based substitution**

少なくとも「主実装と完全に同じコード経路」にはしないでください。

## 提出形式

zip：

```
T2_fixed_point_grok_v2/
├── src/gl/fixed_point.py        # k-decomposition、prover 非依存
├── src/gl/fixed_point_alt.py    # 別経路
├── src/gl/modalized.py
├── tests/test_fixed_point_kats.py
├── tests/test_fixed_point_random.py
├── tests/test_fixed_point_uniqueness.py
└── RESULTS.md                    # 実走結果、X passed、shrink で見つかった失敗例
```

## 心構え

Boolos 1993 そのものは記憶ではアクセスできないことは分かっています。それでも、
**k-decomposition の擬似コード**は上に貼ったので、これに沿って実装してください。
中途半端な hardcode + 構造再帰では他案と統合候補になりません。

期限：可能な限り早めにお願いします。
