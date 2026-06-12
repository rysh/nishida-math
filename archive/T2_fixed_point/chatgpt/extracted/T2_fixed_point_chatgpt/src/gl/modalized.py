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
