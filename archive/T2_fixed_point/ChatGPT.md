# 案 ChatGPT — T2 固定点エンジン

## 0. 自己申告（必須・先頭に置く）

* 確信度：**Medium**
* 不安な箇所（具体的に、最低 3 つ）：

  * Boolos 原文の手順そのものを逐語的には確認できていない。Cambridge Core の章要約と、二次資料上の k-decomposition 記述に基づく再構成である。
  * 実装する k-decomposition が有限サイズの実用 random battery では通る可能性が高い一方、既存 `prove_gl` の性能上限により、大きめのランダム式では timeout / blow-up が起きる可能性がある。
  * `Formula` コンストラクタが内部でどの程度正規化するか不明なので、こちら側に軽い構文簡約を入れた。これは保守的な簡約だが、既存実装と想定がずれる可能性はある。
  * `Box(⊤) → ⊤` を構文簡約として採用している。これは normal modal logic で安全な同値だが、「engine 内で正しさを判定しない」という境界を厳密に読む場合、嫌う reviewer がいる可能性がある。
  * alternative 実装は主実装と同じ k-decomposition 定理に基づくため、完全に独立した理論的アルゴリズムではない。差分は placeholder-based vs path-based である。
* 参照した文献・URL（あれば）：

  * Boolos, *The Logic of Provability*, Chapter 8 “The fixed point theorem” の Cambridge Core 要約。要約部は fixed point theorem が de Jongh / Sambin によるものだと述べ、modalized の定義と固定点の一意性に関する説明を載せている。([Cambridge University Press & Assessment][1])
  * k-decomposition の簡潔な説明がある二次資料。特に `A = B(□D1(p),...,□Dk(p))` と分解し、各 `Bi` の固定点 `Hi` から `H = B(□D1(H1),...,□Dk(Hk))` を構成する形を参照した。([LessWrong][2])
* ハルシネーション可能性が高い記述：

  * 「Boolos のアルゴリズムそのもの」との対応を強く主張する記述。
  * Smoryński / Bernardi / de Jongh の細部の命題番号や証明構造への言及。
  * `prove_gl` の実行性能や既存 26 件との合計 passed 数。
* **特別申告**：

  * Boolos 1993 の該当章を本当に参照したか / 記憶を再構成したか / Web で参照したか：**Web では Cambridge Core の章要約のみ参照。本文全体・原文アルゴリズムは参照していない。実装は記憶と二次資料の k-decomposition sketch から再構成。**
  * Boolos のアルゴリズム原文と自分の実装の対応関係についての確信度：**Medium-Low**。k-decomposition 型の標準的構成としては妥当だが、Boolos 原文の提示順・記法・補題構成と一致するとは断言しない。

## 1. 設計判断（散文、簡潔に）

主実装は **outermost p-box k-decomposition** で書く。`A(p)` の中で `p` を含む最外側の `Box(D_i)` をすべて placeholder に置き換え、`A = B(□D1(p),...,□Dk(p))` とみなす。各 `i` について `Bi = B(□D1(p),...,⊤,...,□Dk(p))` を作り、再帰的に `Hi = fixed_point(Bi,p)` を得る。最後に `H = B(□D1(Hi),...,□Dk(Hk))` を返す。

停止性は、再帰呼び出しごとに最外側の `p` を含む box の個数が 1 つ減ることに依存する。`p` が `□` の下にのみ出現することは `modalized.py` の静的検査で保証する。`fixed_point.py` / `fixed_point_alt.py` は `gl.tableau` と `gl.kripke_search` を import しない。固定点方程式の確認は test 側だけで `prove_gl` に任せる。

`⊤` は `Not(bot())` として表現する。Henkin KAT の期待形をきれいに出すため、保守的な簡約、特に `Box(⊤) -> ⊤`、`Not(⊤) -> ⊥`、命題論理的な定数畳み込みを入れる。

## 2. 疑似コード（言語非依存）

```text
TOP := ¬⊥

is_modalized_in(A, p, depth):
    case A of
      ⊥: true
      atom x: x != p or depth > 0
      ¬B: is_modalized_in(B, p, depth)
      □B: is_modalized_in(B, p, depth + 1)
      B ∧ C / B ∨ C / B → C / B ↔ C:
          all children modalized at same depth

substitute(A, p, H):
    recursively replace atom(p) by H

fixed_point(A, p):
    if not is_modalized_in(A, p):
        raise ValueError
    A := simplify(A)
    if p not in atoms(A):
        return A

    boxes := all outermost subformulas □D such that p occurs in □D
    create fresh placeholders x1...xk
    B := A with each selected □Di replaced by xi

    for each i in 1..k:
        Bi := B with xi := TOP and xj := □Dj for j != i
        Hi := fixed_point(Bi, p)

    H := B with xi := □ substitute(Di, p, Hi)
    return simplify(H)
```

## 3. Python 実装（モジュール単位）

### `src/gl/modalized.py`

```python
from __future__ import annotations

from gl.formula import Formula


def is_modalized_in(A: Formula, p: str) -> bool:
    """Return True iff every occurrence of atom p is in the scope of a Box.

    There are no binders in this Formula language, so this is just an
    occurrence-position check.  Occurrences under one or more boxes are allowed;
    unboxed occurrences are rejected.
    """
    return _is_modalized_in(A, p, box_depth=0)


def _is_modalized_in(f: Formula, p: str, box_depth: int) -> bool:
    match f.type:
        case "bot":
            return True
        case "atom":
            return f.name != p or box_depth > 0
        case "not":
            assert f.arg is not None
            return _is_modalized_in(f.arg, p, box_depth)
        case "box":
            assert f.arg is not None
            return _is_modalized_in(f.arg, p, box_depth + 1)
        case "and" | "or":
            return all(_is_modalized_in(arg, p, box_depth) for arg in f.args)
        case "imp" | "iff":
            assert f.left is not None
            assert f.right is not None
            return (
                _is_modalized_in(f.left, p, box_depth)
                and _is_modalized_in(f.right, p, box_depth)
            )
        case _:
            raise ValueError(f"unknown Formula.type: {f.type!r}")
```

### `src/gl/fixed_point.py`

```python
from __future__ import annotations

from gl.formula import (
    Formula,
    And,
    Box,
    Iff,
    Imp,
    Not,
    Or,
    atom,
    atoms,
    bot,
)
from gl.modalized import is_modalized_in


def fixed_point(A: Formula, p: str) -> Formula:
    """Construct a de Jongh/Sambin-style GL fixed point for A in p.

    Precondition:
        p is modalized in A, i.e. every occurrence of p is under Box.

    Postcondition, to be checked outside this module by an independent prover:
        GL proves H <-> A[p := H].

    This module intentionally does not import gl.tableau or gl.kripke_search.
    """
    if not is_modalized_in(A, p):
        raise ValueError(f"formula is not modalized in {p!r}")

    A = _simplify(A)
    if p not in atoms(A):
        return A

    B, names, Ds = _decompose_outer_p_boxes(A, p)
    if not names:
        # Should be unreachable after is_modalized_in + p in atoms(A), but keep
        # the failure explicit rather than looping silently.
        raise ValueError(f"internal error: no outer p-boxes found for {p!r}")

    Hs: list[Formula] = []
    for i, _name in enumerate(names):
        replacements: dict[str, Formula] = {}
        for j, name in enumerate(names):
            replacements[name] = _top() if i == j else Box(Ds[j])
        Bi = _simplify(_replace_atoms_by_name(B, replacements))
        Hs.append(fixed_point(Bi, p))

    final_replacements = {
        name: Box(_simplify(substitute(Ds[i], p, Hs[i])))
        for i, name in enumerate(names)
    }
    return _simplify(_replace_atoms_by_name(B, final_replacements))


def substitute(formula: Formula, p: str, H: Formula) -> Formula:
    """Substitute all occurrences of atom p in formula by H."""
    match formula.type:
        case "bot":
            return formula
        case "atom":
            return H if formula.name == p else formula
        case "not":
            assert formula.arg is not None
            return Not(substitute(formula.arg, p, H))
        case "box":
            assert formula.arg is not None
            return Box(substitute(formula.arg, p, H))
        case "and":
            return And(*(substitute(arg, p, H) for arg in formula.args))
        case "or":
            return Or(*(substitute(arg, p, H) for arg in formula.args))
        case "imp":
            assert formula.left is not None
            assert formula.right is not None
            return Imp(
                substitute(formula.left, p, H),
                substitute(formula.right, p, H),
            )
        case "iff":
            assert formula.left is not None
            assert formula.right is not None
            return Iff(
                substitute(formula.left, p, H),
                substitute(formula.right, p, H),
            )
        case _:
            raise ValueError(f"unknown Formula.type: {formula.type!r}")


def _top() -> Formula:
    return Not(bot())


def _is_top(f: Formula) -> bool:
    return f == _top()


def _simplify(f: Formula) -> Formula:
    """Small, conservative simplifier.

    This is not a GL decision procedure.  It only normalizes constants and
    syntactic redundancies that keep KAT output readable.
    """
    match f.type:
        case "bot" | "atom":
            return f

        case "not":
            assert f.arg is not None
            arg = _simplify(f.arg)
            if arg.type == "bot":
                return _top()
            if _is_top(arg):
                return bot()
            if arg.type == "not":
                assert arg.arg is not None
                return _simplify(arg.arg)
            return Not(arg)

        case "box":
            assert f.arg is not None
            arg = _simplify(f.arg)
            if _is_top(arg):
                return _top()
            return Box(arg)

        case "and":
            items: list[Formula] = []
            for arg in f.args:
                s = _simplify(arg)
                if s.type == "bot":
                    return bot()
                if _is_top(s):
                    continue
                if s.type == "and":
                    items.extend(s.args)
                else:
                    items.append(s)

            if not items:
                return _top()
            if len(items) == 1:
                return items[0]
            return And(*items)

        case "or":
            items: list[Formula] = []
            for arg in f.args:
                s = _simplify(arg)
                if _is_top(s):
                    return _top()
                if s.type == "bot":
                    continue
                if s.type == "or":
                    items.extend(s.args)
                else:
                    items.append(s)

            if not items:
                return bot()
            if len(items) == 1:
                return items[0]
            return Or(*items)

        case "imp":
            assert f.left is not None
            assert f.right is not None
            left = _simplify(f.left)
            right = _simplify(f.right)

            if left.type == "bot" or _is_top(right):
                return _top()
            if _is_top(left):
                return right
            if right.type == "bot":
                return _simplify(Not(left))
            if left == right:
                return _top()
            return Imp(left, right)

        case "iff":
            assert f.left is not None
            assert f.right is not None
            left = _simplify(f.left)
            right = _simplify(f.right)

            if left == right:
                return _top()
            if _is_top(left):
                return right
            if _is_top(right):
                return left
            if left.type == "bot":
                return _simplify(Not(right))
            if right.type == "bot":
                return _simplify(Not(left))
            return Iff(left, right)

        case _:
            raise ValueError(f"unknown Formula.type: {f.type!r}")


def _decompose_outer_p_boxes(
    A: Formula,
    p: str,
) -> tuple[Formula, list[str], list[Formula]]:
    """Return B, placeholder names, and D_i from A = B(□D_i(p)).

    The selected boxes are the outermost Box-subformulas containing p.  They are
    pairwise disjoint by construction.
    """
    count = _count_outer_p_boxes(A, p)
    names = _fresh_placeholder_names(atoms(A), count)
    Ds: list[Formula] = []
    index = 0

    def go(f: Formula) -> Formula:
        nonlocal index

        if f.type == "box" and p in atoms(f):
            assert f.arg is not None
            name = names[index]
            index += 1
            Ds.append(f.arg)
            return atom(name)

        match f.type:
            case "bot" | "atom":
                return f
            case "not":
                assert f.arg is not None
                return Not(go(f.arg))
            case "box":
                assert f.arg is not None
                return Box(go(f.arg))
            case "and":
                return And(*(go(arg) for arg in f.args))
            case "or":
                return Or(*(go(arg) for arg in f.args))
            case "imp":
                assert f.left is not None
                assert f.right is not None
                return Imp(go(f.left), go(f.right))
            case "iff":
                assert f.left is not None
                assert f.right is not None
                return Iff(go(f.left), go(f.right))
            case _:
                raise ValueError(f"unknown Formula.type: {f.type!r}")

    B = go(A)
    assert index == count
    return B, names, Ds


def _count_outer_p_boxes(f: Formula, p: str) -> int:
    if f.type == "box" and p in atoms(f):
        return 1

    match f.type:
        case "bot" | "atom":
            return 0
        case "not":
            assert f.arg is not None
            return _count_outer_p_boxes(f.arg, p)
        case "box":
            assert f.arg is not None
            return _count_outer_p_boxes(f.arg, p)
        case "and" | "or":
            return sum(_count_outer_p_boxes(arg, p) for arg in f.args)
        case "imp" | "iff":
            assert f.left is not None
            assert f.right is not None
            return _count_outer_p_boxes(f.left, p) + _count_outer_p_boxes(f.right, p)
        case _:
            raise ValueError(f"unknown Formula.type: {f.type!r}")


def _fresh_placeholder_names(used_atoms: frozenset[str], count: int) -> list[str]:
    names: list[str] = []
    i = 0
    while len(names) < count:
        candidate = f"__gl_fp_placeholder_{i}__"
        if candidate not in used_atoms and candidate not in names:
            names.append(candidate)
        i += 1
    return names


def _replace_atoms_by_name(f: Formula, replacements: dict[str, Formula]) -> Formula:
    match f.type:
        case "bot":
            return f
        case "atom":
            assert f.name is not None
            return replacements.get(f.name, f)
        case "not":
            assert f.arg is not None
            return Not(_replace_atoms_by_name(f.arg, replacements))
        case "box":
            assert f.arg is not None
            return Box(_replace_atoms_by_name(f.arg, replacements))
        case "and":
            return And(*(_replace_atoms_by_name(arg, replacements) for arg in f.args))
        case "or":
            return Or(*(_replace_atoms_by_name(arg, replacements) for arg in f.args))
        case "imp":
            assert f.left is not None
            assert f.right is not None
            return Imp(
                _replace_atoms_by_name(f.left, replacements),
                _replace_atoms_by_name(f.right, replacements),
            )
        case "iff":
            assert f.left is not None
            assert f.right is not None
            return Iff(
                _replace_atoms_by_name(f.left, replacements),
                _replace_atoms_by_name(f.right, replacements),
            )
        case _:
            raise ValueError(f"unknown Formula.type: {f.type!r}")
```

### `src/gl/fixed_point_alt.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from gl.formula import (
    Formula,
    And,
    Box,
    Iff,
    Imp,
    Not,
    Or,
    atoms,
    bot,
)
from gl.modalized import is_modalized_in


PathStep = tuple[Literal["arg", "left", "right", "args"], int | None]
Path = tuple[PathStep, ...]


@dataclass(frozen=True, slots=True)
class BoxOccurrence:
    path: Path
    body: Formula


def fixed_point_alt(A: Formula, p: str) -> Formula:
    """Alternative implementation of the same construction.

    Unlike gl.fixed_point.fixed_point, this implementation does not introduce
    placeholder atoms.  It collects paths to outermost p-containing boxes and
    performs simultaneous path replacement.
    """
    if not is_modalized_in(A, p):
        raise ValueError(f"formula is not modalized in {p!r}")

    A = _simplify(A)
    if p not in atoms(A):
        return A

    occs = _outer_p_box_occurrences(A, p)
    if not occs:
        raise ValueError(f"internal error: no outer p-boxes found for {p!r}")

    Hs: list[Formula] = []
    for i, occ in enumerate(occs):
        replacements: dict[Path, Formula] = {
            other.path: (_top() if i == j else Box(other.body))
            for j, other in enumerate(occs)
        }
        Bi = _simplify(_replace_paths(A, replacements))
        Hs.append(fixed_point_alt(Bi, p))

    final_replacements = {
        occ.path: Box(_simplify(_substitute(occ.body, p, Hs[i])))
        for i, occ in enumerate(occs)
    }
    return _simplify(_replace_paths(A, final_replacements))


def _substitute(formula: Formula, p: str, H: Formula) -> Formula:
    match formula.type:
        case "bot":
            return formula
        case "atom":
            return H if formula.name == p else formula
        case "not":
            assert formula.arg is not None
            return Not(_substitute(formula.arg, p, H))
        case "box":
            assert formula.arg is not None
            return Box(_substitute(formula.arg, p, H))
        case "and":
            return And(*(_substitute(arg, p, H) for arg in formula.args))
        case "or":
            return Or(*(_substitute(arg, p, H) for arg in formula.args))
        case "imp":
            assert formula.left is not None
            assert formula.right is not None
            return Imp(_substitute(formula.left, p, H), _substitute(formula.right, p, H))
        case "iff":
            assert formula.left is not None
            assert formula.right is not None
            return Iff(_substitute(formula.left, p, H), _substitute(formula.right, p, H))
        case _:
            raise ValueError(f"unknown Formula.type: {formula.type!r}")


def _outer_p_box_occurrences(A: Formula, p: str) -> list[BoxOccurrence]:
    out: list[BoxOccurrence] = []

    def go(f: Formula, path: Path) -> None:
        if f.type == "box" and p in atoms(f):
            assert f.arg is not None
            out.append(BoxOccurrence(path=path, body=f.arg))
            return

        match f.type:
            case "bot" | "atom":
                return
            case "not":
                assert f.arg is not None
                go(f.arg, path + (("arg", None),))
            case "box":
                assert f.arg is not None
                go(f.arg, path + (("arg", None),))
            case "and" | "or":
                for idx, arg in enumerate(f.args):
                    go(arg, path + (("args", idx),))
            case "imp" | "iff":
                assert f.left is not None
                assert f.right is not None
                go(f.left, path + (("left", None),))
                go(f.right, path + (("right", None),))
            case _:
                raise ValueError(f"unknown Formula.type: {f.type!r}")

    go(A, ())
    return out


def _replace_paths(f: Formula, replacements: dict[Path, Formula]) -> Formula:
    def go(node: Formula, path: Path) -> Formula:
        if path in replacements:
            return replacements[path]

        match node.type:
            case "bot" | "atom":
                return node
            case "not":
                assert node.arg is not None
                return Not(go(node.arg, path + (("arg", None),)))
            case "box":
                assert node.arg is not None
                return Box(go(node.arg, path + (("arg", None),)))
            case "and":
                return And(
                    *(
                        go(arg, path + (("args", idx),))
                        for idx, arg in enumerate(node.args)
                    )
                )
            case "or":
                return Or(
                    *(
                        go(arg, path + (("args", idx),))
                        for idx, arg in enumerate(node.args)
                    )
                )
            case "imp":
                assert node.left is not None
                assert node.right is not None
                return Imp(
                    go(node.left, path + (("left", None),)),
                    go(node.right, path + (("right", None),)),
                )
            case "iff":
                assert node.left is not None
                assert node.right is not None
                return Iff(
                    go(node.left, path + (("left", None),)),
                    go(node.right, path + (("right", None),)),
                )
            case _:
                raise ValueError(f"unknown Formula.type: {node.type!r}")

    return go(f, ())


def _top() -> Formula:
    return Not(bot())


def _is_top(f: Formula) -> bool:
    return f == _top()


def _simplify(f: Formula) -> Formula:
    match f.type:
        case "bot" | "atom":
            return f

        case "not":
            assert f.arg is not None
            arg = _simplify(f.arg)
            if arg.type == "bot":
                return _top()
            if _is_top(arg):
                return bot()
            if arg.type == "not":
                assert arg.arg is not None
                return _simplify(arg.arg)
            return Not(arg)

        case "box":
            assert f.arg is not None
            arg = _simplify(f.arg)
            if _is_top(arg):
                return _top()
            return Box(arg)

        case "and":
            items: list[Formula] = []
            for arg in f.args:
                s = _simplify(arg)
                if s.type == "bot":
                    return bot()
                if _is_top(s):
                    continue
                if s.type == "and":
                    items.extend(s.args)
                else:
                    items.append(s)
            if not items:
                return _top()
            if len(items) == 1:
                return items[0]
            return And(*items)

        case "or":
            items: list[Formula] = []
            for arg in f.args:
                s = _simplify(arg)
                if _is_top(s):
                    return _top()
                if s.type == "bot":
                    continue
                if s.type == "or":
                    items.extend(s.args)
                else:
                    items.append(s)
            if not items:
                return bot()
            if len(items) == 1:
                return items[0]
            return Or(*items)

        case "imp":
            assert f.left is not None
            assert f.right is not None
            left = _simplify(f.left)
            right = _simplify(f.right)
            if left.type == "bot" or _is_top(right):
                return _top()
            if _is_top(left):
                return right
            if right.type == "bot":
                return _simplify(Not(left))
            if left == right:
                return _top()
            return Imp(left, right)

        case "iff":
            assert f.left is not None
            assert f.right is not None
            left = _simplify(f.left)
            right = _simplify(f.right)
            if left == right:
                return _top()
            if _is_top(left):
                return right
            if _is_top(right):
                return left
            if left.type == "bot":
                return _simplify(Not(right))
            if right.type == "bot":
                return _simplify(Not(left))
            return Iff(left, right)

        case _:
            raise ValueError(f"unknown Formula.type: {f.type!r}")
```

## 4. テスト（pytest 形式）

### `tests/test_fixed_point_kats.py`

```python
from __future__ import annotations

import ast
import inspect

import pytest

import gl.fixed_point as fixed_point_module
import gl.fixed_point_alt as fixed_point_alt_module
from gl.fixed_point import fixed_point, substitute
from gl.formula import Box, Iff, Imp, Not, atom, atoms, bot
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl


def assert_fixed_point(A, p, expected_H):
    H = fixed_point(A, p)

    assert p not in atoms(H)

    equiv_to_expected = Iff(H, expected_H)
    assert prove_gl(equiv_to_expected).status == "proved", (
        f"H not GL-equivalent to expected: {H} vs {expected_H}"
    )

    fp_equation = Iff(H, substitute(A, p, H))
    assert prove_gl(fp_equation).status == "proved", (
        f"GL ⊬ H ↔ A[p:=H]: H={H}"
    )


def test_engine_modules_do_not_import_provers():
    for module in (fixed_point_module, fixed_point_alt_module):
        tree = ast.parse(inspect.getsource(module))
        imported_modules = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)

        assert "gl.tableau" not in imported_modules
        assert "gl.kripke_search" not in imported_modules


def test_modalized_rejects_free_p():
    assert not is_modalized_in(atom("p"), "p")
    assert not is_modalized_in(Imp(atom("p"), Box(atom("p"))), "p")
    assert is_modalized_in(Imp(atom("q"), Box(atom("p"))), "p")

    with pytest.raises(ValueError):
        fixed_point(atom("p"), "p")


def test_godel_fixed_point():
    """KAT 1.

    For H = ¬□⊥, the fixed-point equation is H ↔ ¬□H.

    The intended GL verification reduces to □⊥ ↔ □¬□⊥:
    - left-to-right: from □⊥ by normal modal monotonicity;
    - right-to-left: ¬□⊥ is □⊥→⊥, so □¬□⊥ is □(□⊥→⊥);
      Löb with A:=⊥ yields □(□⊥→⊥)→□⊥.
    The test itself does not encode this derivation; it asks the independent
    tableau prover to certify the biconditional.
    """
    A = Not(Box(atom("p")))
    assert_fixed_point(A, "p", Not(Box(bot())))


def test_henkin_fixed_point():
    A = Box(atom("p"))
    assert_fixed_point(A, "p", Not(bot()))


def test_lob_sentence_fixed_point():
    A = Imp(Box(atom("p")), atom("q"))
    assert_fixed_point(A, "p", Imp(Box(atom("q")), atom("q")))


def test_box_not_fixed_point():
    A = Box(Not(atom("p")))
    assert_fixed_point(A, "p", Box(bot()))
```

### `tests/test_fixed_point_random.py`

```python
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from gl.fixed_point import fixed_point, substitute
from gl.formula import And, Box, Iff, Imp, Not, Or, atom, atoms, bot, modal_depth
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl


TOP = Not(bot())
P_NAME = "p"
EXTRA_ATOMS = ("q", "r")


@st.composite
def modalized_formula_strategy(
    draw,
    *,
    size: int = 5,
    boxes_left: int = 3,
    under_box: bool = False,
):
    """Generate formulas modalized in p without filtering.

    The generator tracks whether the current position is already under a Box.
    atom("p") is only offered when under_box=True.
    """
    base_atoms = [atom(name) for name in EXTRA_ATOMS]
    if under_box:
        base_atoms.append(atom(P_NAME))

    base = st.one_of(
        st.sampled_from([bot(), TOP]),
        st.sampled_from(base_atoms),
    )

    if size <= 0:
        return draw(base)

    constructors = ["base", "not", "and", "or", "imp", "iff"]
    if boxes_left > 0:
        constructors.append("box")

    choice = draw(st.sampled_from(constructors))

    if choice == "base":
        return draw(base)

    if choice == "not":
        inner = draw(
            modalized_formula_strategy(
                size=size - 1,
                boxes_left=boxes_left,
                under_box=under_box,
            )
        )
        return Not(inner)

    if choice == "box":
        inner = draw(
            modalized_formula_strategy(
                size=size - 1,
                boxes_left=boxes_left - 1,
                under_box=True,
            )
        )
        return Box(inner)

    left_size = max(size - 1, 0)
    right_size = max(size - 2, 0)

    left = draw(
        modalized_formula_strategy(
            size=left_size,
            boxes_left=boxes_left,
            under_box=under_box,
        )
    )
    right = draw(
        modalized_formula_strategy(
            size=right_size,
            boxes_left=boxes_left,
            under_box=under_box,
        )
    )

    if choice == "and":
        return And(left, right)
    if choice == "or":
        return Or(left, right)
    if choice == "imp":
        return Imp(left, right)
    if choice == "iff":
        return Iff(left, right)

    raise AssertionError(f"unknown strategy choice: {choice!r}")


@given(A=modalized_formula_strategy())
@settings(max_examples=225, deadline=None)
def test_random_modalized_fixed_points_are_proved_by_independent_tableau(A):
    assert is_modalized_in(A, P_NAME)
    assert modal_depth(A) <= 3

    H = fixed_point(A, P_NAME)

    assert P_NAME not in atoms(H)

    fp_equation = Iff(H, substitute(A, P_NAME, H))
    result = prove_gl(fp_equation)

    assert result.status == "proved", (
        "independent prover did not certify fixed-point equation; "
        f"A={A!r}; H={H!r}; result={result!r}"
    )
```

### `tests/test_fixed_point_uniqueness.py`

```python
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from gl.fixed_point import fixed_point
from gl.fixed_point_alt import fixed_point_alt
from gl.formula import And, Box, Iff, Imp, Not, Or, atom, atoms, bot, modal_depth
from gl.modalized import is_modalized_in
from gl.tableau import prove_gl


TOP = Not(bot())
P_NAME = "p"
EXTRA_ATOMS = ("q", "r")


def assert_algorithms_agree_up_to_gl(A):
    H1 = fixed_point(A, P_NAME)
    H2 = fixed_point_alt(A, P_NAME)

    assert P_NAME not in atoms(H1)
    assert P_NAME not in atoms(H2)

    result = prove_gl(Iff(H1, H2))
    assert result.status == "proved", (
        "main and alternative fixed-point engines disagree up to GL; "
        f"A={A!r}; H1={H1!r}; H2={H2!r}; result={result!r}"
    )


def test_known_answer_outputs_agree_up_to_gl():
    cases = [
        Not(Box(atom("p"))),
        Box(atom("p")),
        Imp(Box(atom("p")), atom("q")),
        Box(Not(atom("p"))),
    ]
    for A in cases:
        assert_algorithms_agree_up_to_gl(A)


@st.composite
def modalized_formula_strategy(
    draw,
    *,
    size: int = 5,
    boxes_left: int = 3,
    under_box: bool = False,
):
    base_atoms = [atom(name) for name in EXTRA_ATOMS]
    if under_box:
        base_atoms.append(atom(P_NAME))

    base = st.one_of(
        st.sampled_from([bot(), TOP]),
        st.sampled_from(base_atoms),
    )

    if size <= 0:
        return draw(base)

    constructors = ["base", "not", "and", "or", "imp", "iff"]
    if boxes_left > 0:
        constructors.append("box")

    choice = draw(st.sampled_from(constructors))

    if choice == "base":
        return draw(base)

    if choice == "not":
        return Not(
            draw(
                modalized_formula_strategy(
                    size=size - 1,
                    boxes_left=boxes_left,
                    under_box=under_box,
                )
            )
        )

    if choice == "box":
        return Box(
            draw(
                modalized_formula_strategy(
                    size=size - 1,
                    boxes_left=boxes_left - 1,
                    under_box=True,
                )
            )
        )

    left = draw(
        modalized_formula_strategy(
            size=max(size - 1, 0),
            boxes_left=boxes_left,
            under_box=under_box,
        )
    )
    right = draw(
        modalized_formula_strategy(
            size=max(size - 2, 0),
            boxes_left=boxes_left,
            under_box=under_box,
        )
    )

    if choice == "and":
        return And(left, right)
    if choice == "or":
        return Or(left, right)
    if choice == "imp":
        return Imp(left, right)
    if choice == "iff":
        return Iff(left, right)

    raise AssertionError(f"unknown strategy choice: {choice!r}")


@given(A=modalized_formula_strategy())
@settings(max_examples=225, deadline=None)
def test_random_main_and_alt_outputs_are_gl_equivalent(A):
    assert is_modalized_in(A, P_NAME)
    assert modal_depth(A) <= 3
    assert_algorithms_agree_up_to_gl(A)
```

## 5. 自分の実装をデバッグする手順

1. まず `tests/test_fixed_point_kats.py` だけを走らせる。

```bash
uv run pytest -q tests/test_fixed_point_kats.py
```

2. Henkin KAT が落ちる場合は、`Box(⊤) -> ⊤` の簡約が働いているか確認する。`fixed_point(Box(atom("p")), "p")` が `Not(bot())` またはそれと GL-equivalent な式になっていればよい。

3. Gödel KAT が落ちる場合は、`Not(Box(atom("p")))` の decomposition が `B(x)=¬x, D1=p` になっているか確認する。`B1=¬⊤=⊥`、`H1=⊥`、最終 `H=¬□⊥` でなければ decomposition が誤っている。

4. `Box(Not(atom("p")))` が落ちる場合は、`B(x)=x, D1=¬p`、`B1=⊤`、`H1=⊤`、最終 `H=□¬⊤=□⊥` になっているか確認する。

5. random が落ちたら Hypothesis の shrink 結果を見て、次の 3 点を確認する。

   * `is_modalized_in(A, "p")` が本当に True か。
   * `fixed_point(A,"p")` の返り値に `p` が残っていないか。
   * `fixed_point.py` が prover を呼んでいないかではなく、test 側の `prove_gl(Iff(H, substitute(A,p,H)))` が失敗しているか。

6. 主実装と alt 実装の一致テストが落ちる場合は、まず KAT 4 例で `repr(H1)` と `repr(H2)` を比較する。KAT で一致し、random だけ落ちるなら、path replacement の `Path` 構築が `and` / `or` の n-ary `args` で壊れている可能性が高い。

## 6. 既知の限界・未実装

* Boolos 原文に忠実な章番号・補題番号つき実装ではない。k-decomposition 型の構成的アルゴリズムとして実装している。
* `fixed_point_alt.py` は path-based なので主実装とは異なるコード経路を通るが、同じ数学的構成に依存している。完全に別系統、たとえば trace / normal-form based algorithm ではない。
* 式サイズの爆発に対する対策はない。random strategy は `size=5`, `modal_depth<=3` に制限して prover 負荷を抑えている。
* Hypothesis が dev dependency にない場合は、`pyproject.toml` 側に `hypothesis` を追加する必要がある。
* `Box(⊤) -> ⊤` などの簡約を実装内に入れている。これは fixed-point equation の独立検証ではないが、review 方針によっては簡約を最小化して prover に任せる設計のほうが好まれるかもしれない。
* `⊤` 専用 constructor がない前提で `Not(bot())` を使う。既存 `Formula` 側に将来 `top` 型が追加されると、このコードは更新が必要。

## 7. 他案と差分が出そうなポイント（予想 3 つ）

1. **Boolos アルゴリズムの定式化**
   この案は k-decomposition を採用した。他案は trace / rank normal form、Smoryński 風、あるいは Bernardi uniqueness からの構成を選ぶ可能性がある。

2. **簡約の強さ**
   この案は KAT の可読性のため `Box(⊤)->⊤` まで簡約する。他案は純粋構成に寄せて `Box(Not(bot()))` をそのまま返し、expected との一致を prover に完全委譲するかもしれない。

3. **第 2 アルゴリズムの独立性**
   この案の alt は placeholder ではなく path replacement で書いたが、同じ k-decomposition 定理に基づく。他案は本当に別系統の trace algorithm を入れるかもしれない。その場合、uniqueness test の価値は高くなるが、実装難度とバグ率も上がる。

実行結果：**未実行**。この回答生成環境には対象リポジトリと既存 `gl.tableau.prove_gl` がないため、`X passed` は正直には申告できない。期待される確認コマンドは次です。

```bash
uv run pytest -q
```

[1]: https://www.cambridge.org/core/books/logic-of-provability/fixed-point-theorem/597E0CCE3CE6D6270005EBBC28988530 "The fixed point theorem (Chapter 8) - The Logic of Provability"
[2]: https://www.lesswrong.com/w/fixed-point-theorem-of-provability-logic "Fixed point theorem of provability logic — LessWrong"
