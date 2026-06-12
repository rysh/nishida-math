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
