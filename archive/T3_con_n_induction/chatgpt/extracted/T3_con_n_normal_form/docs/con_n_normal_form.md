# T3: `Con_n` の正規形 `Con_n \equiv \neg\Box^{n+1}\bot`

> 注: この実行環境には `_shared/preamble.md` と `_shared/triangulate_output_format.md` の実体が見つからなかったため、本文は本タスクの要求構造に従って単体で読める形にしている。リポジトリに配置する際は、必要ならこのファイル冒頭にその 2 ファイルの内容をそのまま前置する。

## §0 自己申告

### off-by-one を自分が踏みうる箇所

1. 正規形の指数を `Con_n \equiv \neg\Box^n\bot` と 1 つ小さく書く箇所。正しくは `Con_n \equiv \neg\Box^{n+1}\bot`。
2. 帰納 step の結論を `\neg\Box^{n+1}\bot` のままにする箇所。`Con_{n+1}` の正規形は `\neg\Box^{(n+1)+1}\bot = \neg\Box^{n+2}\bot`。
3. `\neg Con_n \equiv \Box^{n+1}\bot` を得る段階で、`\neg\neg\Box^{n+1}\bot` の二重否定除去を忘れる箇所。
4. monotone 証明で `\Box^{n+1}\bot \to \Box^{n+2}\bot` を 4 公理の `n+1` 回適用と書く箇所。正しくは、`A := \Box^n\bot` に対する 4 の **1 インスタンス** `\Box A \to \Box\Box A`。
5. strict 反例の世界数を `n+1` 個または `n+3` 個にする箇所。正しくは、root から終端まで **`n+2` 個の世界**。
6. strict 反例で反証対象を monotone 方向 `Con_{n+1}\to Con_n` にしてしまう箇所。反証対象は strict 方向 `Con_n\to Con_{n+1}`。
7. strict 反例で `rel` を隣接辺だけにして、検証器が推移閉包を取らない場合に GL フレーム条件を落とす箇所。ここでは `rel` に推移閉包を明示的に入れる。
8. `\Box^k\bot` の成立条件を「長さ `k` の鎖がある」と逆に読む箇所。正しくは、`\Box^k\bot` は「長さ `k` の `R`-鎖が存在しない」ことを表す。

### 本稿作成時に書き直した箇所

- before: monotone 証明を「`\Box`-単調性で `\Box^{n+1}\bot \to \Box^{n+2}\bot`」と書く形。
  after: `A := \Box^n\bot` に対する 4 公理 `\Box A\to\Box\Box A` の 1 インスタンスであり、`A\to\Box A` でも正規性の単調性でもない、と明示した。
- before: strict 反例の鎖長を「長さ `n+2`」とだけ書き、世界数なのか辺数なのかを曖昧にする形。
  after: 「root から終端まで `n+2` 個の世界、最大 `R`-鎖は `n+1` 本の辺」と明示した。
- before: 帰納 step の `\neg Con_n \equiv \Box^{n+1}\bot` を「同値の箱内代入」と混ぜて書く形。
  after: まず命題論理だけで `\neg Con_n \leftrightarrow \Box^{n+1}\bot` を得て、その後にだけ `\Box`-合同性を使う形へ分離した。

## §1 記法と区別

`\Box^0 A := A`、`\Box^{k+1}A := \Box(\Box^k A)` と定義する。

`Con_n` は次で再帰的に定義される。

\[
Con_0 := \neg\Box\bot,
\qquad
Con_{n+1} := \neg\Box\neg Con_n.
\]

本稿では次の 3 種類を区別する。

1. **定義上の等号** `:=` または `=`: `Con_{n+1}` を `\neg\Box\neg Con_n` と展開するようなメタ言語上の定義展開。
2. **命題論理的変形**: すでに得た同値 `P\leftrightarrow\neg Q` から、古典命題論理だけで `\neg P\leftrightarrow Q` を得る変形。これは `\Box` の規則を使わない。
3. **GL-同値**: `GL\vdash A\leftrightarrow B`。この同値を `\Box` の内側へ入れるには、GL が正規様相論理であることから得られる `\Box`-合同性を使う。

使う補題を明示する。

**補題 1（命題的否定取り）.** 古典命題論理で

\[
(P\leftrightarrow\neg Q)\to(\neg P\leftrightarrow Q)
\]

はトートロジーである。したがって、`GL\vdash P\leftrightarrow\neg Q` なら、命題論理と Modus Ponens だけで

\[
GL\vdash \neg P\leftrightarrow Q
\]

が従う。この段階では `\Box` の規則は使わない。

**補題 2（`\Box`-合同性）.** `GL\vdash A\leftrightarrow B` なら

\[
GL\vdash \Box A\leftrightarrow\Box B.
\]

理由: `A\to B` と `B\to A` にそれぞれ Necessitation を適用し、K 公理

\[
\Box(A\to B)\to(\Box A\to\Box B)
\]

を使う。これは正規様相論理としての GL の性質であり、Löb 公理は使わない。また、これは `A\to\Box A` ではない。

## §2 定理: `Con_n \equiv \neg\Box^{n+1}\bot`

### 主張

すべての `n\ge 0` について、

\[
GL\vdash Con_n\leftrightarrow\neg\Box^{n+1}\bot.
\]

### Base case: `n=0`

定義より

\[
Con_0 := \neg\Box\bot.
\]

また `\Box^{0+1}\bot = \Box^1\bot = \Box\bot` である。したがって

\[
Con_0 = \neg\Box\bot = \neg\Box^{0+1}\bot.
\]

ゆえに同一式の反射性、または命題論理のトートロジー `A\leftrightarrow A` により、

\[
GL\vdash Con_0\leftrightarrow\neg\Box^{0+1}\bot.
\]

### Induction step

帰納法の仮定として、ある `n\ge 0` について

\[
GL\vdash Con_n\leftrightarrow\neg\Box^{n+1}\bot
\tag{IH}
\]

を仮定する。示すべきことは

\[
GL\vdash Con_{n+1}\leftrightarrow\neg\Box^{n+2}\bot
\]

である。

`B_n := \Box^{n+1}\bot` とおく。すると (IH) は

\[
GL\vdash Con_n\leftrightarrow\neg B_n
\]

である。

補題 1 を `P := Con_n`, `Q := B_n` に適用する。これは純粋に命題論理的な変形なので、ここでは `\Box` の単調性・合同性・Necessitation・Löb は使わない。得られるのは

\[
GL\vdash \neg Con_n\leftrightarrow B_n.
\tag{1}
\]

次に、(1) に補題 2 の `\Box`-合同性を適用する。

\[
GL\vdash \Box\neg Con_n\leftrightarrow\Box B_n.
\tag{2}
\]

ここで初めて `\Box` の下への移行を使っている。使用しているのは K と Necessitation から導かれる正規性であり、Löb 公理ではない。

(2) に命題論理のトートロジー `(X\leftrightarrow Y)\to(\neg X\leftrightarrow\neg Y)` を適用して、

\[
GL\vdash \neg\Box\neg Con_n\leftrightarrow\neg\Box B_n.
\tag{3}
\]

定義より

\[
Con_{n+1} := \neg\Box\neg Con_n.
\tag{4}
\]

また `B_n = \Box^{n+1}\bot` なので、

\[
\Box B_n
= \Box(\Box^{n+1}\bot)
= \Box^{n+2}\bot.
\tag{5}
\]

(3), (4), (5) より、

\[
GL\vdash Con_{n+1}\leftrightarrow\neg\Box^{n+2}\bot.
\]

以上で帰納 step が完了する。

### 使用した原理の一覧

この正規形証明で使ったものは次だけである。

- 定義展開: `Con_0`, `Con_{n+1}`, `\Box^k` の定義。
- 古典命題論理: 否定取り、二重否定除去、同値への否定付加。
- GL の正規性: `GL\vdash A\leftrightarrow B` から `GL\vdash\Box A\leftrightarrow\Box B`。

この正規形証明では Löb 公理も 4 公理も使わない。

## §3 pytest による `n=0..8` の正規形検証

`tests/test_con_n_normal_form.py` は次を検証する。

\[
GL\vdash Con_n\leftrightarrow\neg\Box^{n+1}\bot
\qquad(n=0,1,\dots,8).
\]

テスト対象式は再帰定義から直接作った `Con(n)` と、正規形 `neg(box_n(bot(), n + 1))` の `iff` である。つまり、紙の証明で使った正規形を Python 側で事前展開して同一視するのではなく、定義通りの `Con_n` と正規形を T1 の `prove_gl` に渡している。

## §4 Monotone: `Con_{n+1}\to Con_n`

### 主張

すべての `n\ge 0` について、

\[
GL\vdash Con_{n+1}\to Con_n.
\]

### 正規形による証明

§2 より、

\[
GL\vdash Con_{n+1}\leftrightarrow\neg\Box^{n+2}\bot,
\qquad
GL\vdash Con_n\leftrightarrow\neg\Box^{n+1}\bot.
\]

したがって、十分なのは

\[
GL\vdash \neg\Box^{n+2}\bot\to\neg\Box^{n+1}\bot
\tag{M}
\]

を示すことである。

(M) は、古典命題論理上、次の対偶から従う。

\[
GL\vdash \Box^{n+1}\bot\to\Box^{n+2}\bot.
\tag{4_n}
\]

ここで使うのは、GL で導出可能な 4 公理

\[
\Box A\to\Box\Box A
\tag{4}
\]

である。GL を K + Löb で公理化している場合、4 は Löb から導出可能な標準補題である。

`A := \Box^n\bot` と置くと、4 の **1 インスタンス** は

\[
\Box(\Box^n\bot)\to\Box\Box(\Box^n\bot),
\]

すなわち

\[
\Box^{n+1}\bot\to\Box^{n+2}\bot.
\]

これが `(4_n)` である。したがって命題論理の対偶により (M) が従い、正規形同値との含意の推移により

\[
GL\vdash Con_{n+1}\to Con_n
\]

が得られる。

### ここで使っていないもの

- `A\to\Box A` は使わない。これは反射性に近い強い原理で、GL では一般には成立しない。
- 正規性の単調性 `GL\vdash A\to B` なら `GL\vdash\Box A\to\Box B` は、この箇所の本質ではない。
- `\Box^{n+1}\bot\to\Box^{n+2}\bot` は 4 公理の `n+1` 回適用ではない。`A := \Box^n\bot` への 1 回のインスタンス化と、含意の推移・Modus Ponens だけで足りる。

## §5 Strict: `Con_n\to Con_{n+1}` は GL で証明不可

### 反証対象

strict 方向の対象は

\[
Con_n\to Con_{n+1}
\]

である。正規形を使うと、これは

\[
\neg\Box^{n+1}\bot\to\neg\Box^{n+2}\bot.
\tag{S}
\]

この式の対偶は

\[
\Box^{n+2}\bot\to\Box^{n+1}\bot.
\tag{S^\ast}
\]

したがって、反例モデルでは root で

\[
\Box^{n+2}\bot \quad\text{が真、かつ}\quad \Box^{n+1}\bot \quad\text{が偽}
\]

になればよい。同値に、root で `Con_n` が真、`Con_{n+1}` が偽になる。

### 最小反例モデル

`m := n+2` とする。有限線形 GL フレーム `L_m` を次で定義する。

- worlds: `w_0,w_1,\dots,w_{m-1}`。
- root: `w_0`。
- relation: `w_i R w_j` iff `i<j`。
- valuation: 空。今回の式に命題変数は現れない。

この `R` は隣接関係ではなく、**推移閉包込み**である。つまり `w_0 R w_1` と `w_1 R w_2` だけでなく、`w_0 R w_2` も明示的に含める。

`L_m` は有限・推移的・非反射的であるため、GL の有限 Kripke 反例として使える。

### `\Box^k\bot` の成立条件

`L_m` の `w_i` から終端まで残っている世界数は `m-i` 個であり、最大の `R`-鎖の辺数は `m-1-i` である。一般に

\[
L_m,w_i\vDash \Box^k\bot
\quad\Longleftrightarrow\quad
\text{`w_i` から長さ `k` の `R`-鎖が存在しない}
\]

なので、線形鎖では

\[
L_m,w_i\vDash \Box^k\bot
\quad\Longleftrightarrow\quad
m-1-i < k
\quad\Longleftrightarrow\quad
m-i\le k.
\tag{C}
\]

root `w_0` では、`m=n+2` だから

\[
L_{n+2},w_0\vDash \Box^{n+2}\bot
\]

である。一方、`m=n+2>n+1` なので (C) より

\[
L_{n+2},w_0\nvDash \Box^{n+1}\bot.
\]

したがって root で

\[
L_{n+2},w_0\vDash \neg\Box^{n+1}\bot
\quad\text{かつ}\quad
L_{n+2},w_0\nvDash \neg\Box^{n+2}\bot.
\]

正規形により、

\[
L_{n+2},w_0\vDash Con_n
\quad\text{かつ}\quad
L_{n+2},w_0\nvDash Con_{n+1}.
\]

ゆえに

\[
L_{n+2},w_0\nvDash Con_n\to Con_{n+1}.
\]

従って `GL\nvdash Con_n\to Con_{n+1}` である。

### `n=0..4` の JSON artifact

`experiments/wp3/countermodels/strict_n0.json` から `strict_n4.json` までを生成する。各 JSON は次の schema を使う。

```json
{
  "worlds": ["w0", "w1"],
  "root": "w0",
  "rel": [["w0", "w1"]],
  "valuation": {}
}
```

`n` が増えると worlds は `n+2` 個になり、`rel` は `i<j` の全ペアを含む。

## §6 pytest による monotone / strict 検証

`tests/test_con_n_monotone.py` は、`n=0..8` について

\[
GL\vdash Con_{n+1}\to Con_n
\]

を `prove_gl` で検証する。

`tests/test_con_n_strict.py` は、`n=0..4` について JSON 反例モデルを読み込み、反証対象

\[
Con_n\to Con_{n+1}
\]

を T1 の `verify_countermodel` に渡して、root で偽になることを検証する。さらに、JSON が `n+2` 個の世界を持つこと、`rel` が推移閉包込みの線形順序 `i<j` になっていることもテスト側で確認する。

## §7 差が出やすい論点の確認

1. **帰納 step での境界**: `Con_n\leftrightarrow\neg\Box^{n+1}\bot` から `\neg Con_n\leftrightarrow\Box^{n+1}\bot` を得る部分は命題論理だけである。外側の `\Box` に入れる段階だけが GL の正規性、すなわち `\Box`-合同性を使う。
2. **Löb の不使用**: 正規形の帰納証明では Löb は使わない。monotone 証明でのみ、GL 内で導出可能な 4 公理 `\Box A\to\Box\Box A` を使う。
3. **4 公理の適用回数**: `\Box^{n+1}\bot\to\Box^{n+2}\bot` は、`A:=\Box^n\bot` に対する 4 の 1 インスタンスである。「`n+1` 回の 4 適用」ではない。
4. **単調性との混同**: 正規性の単調性は `GL\vdash A\to B` から `GL\vdash\Box A\to\Box B` を得る規則である。monotone 証明に必要な `\Box^{n+1}\bot\to\Box^{n+2}\bot` はこれではなく 4 である。まして `A\to\Box A` ではない。
5. **strict の対象**: 証明不可なのは `Con_n\to Con_{n+1}`、すなわち `\neg\Box^{n+1}\bot\to\neg\Box^{n+2}\bot` である。monotone 方向の否定ではない。
6. **最小反例の世界数**: `Con_n\to Con_{n+1}` の最小反例は `n+2` 個の世界からなる線形鎖である。root から終端までの世界数が `n+2`、最大辺数が `n+1`。このため root で `\Box^{n+2}\bot` は真、`\Box^{n+1}\bot` は偽になる。
7. **`rel` の推移閉包**: JSON では `rel` に `i<j` の全ペアを入れる。検証器が closure を取るかどうかに依存しないようにするためであり、GL フレーム条件の推移性も artifact 単体で読める。
8. **反例モデルの向き**: root が「長い側」ではなく、root から下流に `n+1` 辺だけ進める構造である。`\Box^k\bot` は深さが `k` 未満で真になるため、`k=n+2` で真、`k=n+1` で偽という境界を作る。
