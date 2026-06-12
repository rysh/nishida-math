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
