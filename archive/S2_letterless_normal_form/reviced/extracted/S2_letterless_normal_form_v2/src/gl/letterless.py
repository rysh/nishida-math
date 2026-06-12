"""Letterless normal-form reducer for GL.

This module is deliberately independent of the GL proof engines.  The reducer
computes a canonical closed-fragment normal form internally; tests are
responsible for independently checking GL-provable equivalence by calling a
prover.

Semantic representation
-----------------------
For the closed fragment of GL, a formula can be evaluated by its truth set over
natural-number ranks.  The generator

    B_n = box_power(bot(), n)

is interpreted as the initial segment {0, ..., n-1}.  Thus B_0 is empty,
B_1 is {0}, and Not(bot()) is the whole rank set.  Boolean connectives are set
operations on finite unions of half-open intervals.  For a set S, Box(S) is
computed by the first-gap rule: if g is the least natural number not in S, then
Box(S) = {0, ..., g}; if S is all of N, then Box(S) is all of N.
"""

from __future__ import annotations

import json
from typing import TypeAlias

from gl.formula import And, Formula, Not, Or, bot, box_power

End: TypeAlias = int | None
Interval: TypeAlias = tuple[int, End]
Intervals: TypeAlias = tuple[Interval, ...]

_EMPTY: Intervals = ()
_UNIVERSE: Intervals = ((0, None),)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_letterless(F: Formula) -> bool:
    """Return True iff ``F`` contains no atom node."""

    kind, children = _view(F)
    if kind == "atom":
        return False
    return all(is_letterless(child) for child in children)


def letterless_normal_form(F: Formula) -> Formula:
    """Return a canonical Boolean combination of ``box_power(bot(), n)``.

    ``ValueError`` is raised if ``F`` contains any atom.  This function does not
    import or call ``gl.tableau``, ``gl.kripke_search``, or any other GL prover.
    """

    if not is_letterless(F):
        raise ValueError("letterless_normal_form expects a formula with no atoms")
    return _intervals_to_formula(_eval(F))


def nf_equiv(F1: Formula, F2: Formula) -> bool:
    """Decide GL-equivalence of two letterless formulas by normal-form equality.

    Both inputs are reduced first; the resulting formulas are compared via their
    deterministic ``to_json()`` representation, not by object identity.
    """

    if not is_letterless(F1) or not is_letterless(F2):
        raise ValueError("nf_equiv expects two formulas with no atoms")
    nf1 = letterless_normal_form(F1)
    nf2 = letterless_normal_form(F2)
    return _json_key(nf1) == _json_key(nf2)


# ---------------------------------------------------------------------------
# Direct Formula reader
# ---------------------------------------------------------------------------


def _view(f: Formula) -> tuple[str, tuple[Formula, ...]]:
    """Return ``(f.type, children)`` using the repository's fixed Formula schema."""

    kind = f.type

    if kind in {"bot", "atom"}:
        return kind, ()

    if kind in {"not", "box"}:
        if f.arg is None:
            raise TypeError(f"{kind!r} formula has no arg")
        return kind, (f.arg,)

    if kind in {"and", "or"}:
        return kind, f.args

    if kind in {"imp", "iff"}:
        if f.left is None or f.right is None:
            raise TypeError(f"{kind!r} formula requires left and right children")
        return kind, (f.left, f.right)

    raise TypeError(f"unsupported formula node type: {kind!r}")


# ---------------------------------------------------------------------------
# Closed-fragment interval semantics
# ---------------------------------------------------------------------------


def _eval(f: Formula) -> Intervals:
    kind, children = _view(f)

    if kind == "bot":
        return _EMPTY
    if kind == "atom":
        raise ValueError("letterless_normal_form expects a formula with no atoms")

    if kind == "not":
        return _complement(_eval(children[0]))

    if kind == "and":
        result = _UNIVERSE
        for child in children:
            result = _intersection(result, _eval(child))
        return result

    if kind == "or":
        result = _EMPTY
        for child in children:
            result = _union(result, _eval(child))
        return result

    if kind == "imp":
        left, right = children
        return _union(_complement(_eval(left)), _eval(right))

    if kind == "iff":
        left = _eval(children[0])
        right = _eval(children[1])
        return _union(_intersection(left, right), _intersection(_complement(left), _complement(right)))

    if kind == "box":
        return _box(_eval(children[0]))

    raise TypeError(f"unsupported formula node type: {kind!r}")


def _box(s: Intervals) -> Intervals:
    """Modal box on rank sets, using the first missing lower-rank gap."""

    first_gap = 0
    for start, end in s:
        if start > first_gap:
            break
        if end is None:
            return _UNIVERSE
        if end > first_gap:
            first_gap = end
    return _normalize(((0, first_gap + 1),))


def _union(a: Intervals, b: Intervals) -> Intervals:
    return _normalize((*a, *b))


def _intersection(a: Intervals, b: Intervals) -> Intervals:
    out: list[Interval] = []
    i = j = 0
    while i < len(a) and j < len(b):
        a_start, a_end = a[i]
        b_start, b_end = b[j]
        start = max(a_start, b_start)
        end = _min_end(a_end, b_end)
        if end is None or start < end:
            out.append((start, end))

        if _end_leq(a_end, b_end):
            i += 1
        if _end_leq(b_end, a_end):
            j += 1
    return _normalize(tuple(out))


def _complement(s: Intervals) -> Intervals:
    if not s:
        return _UNIVERSE

    out: list[Interval] = []
    cursor = 0
    for start, end in s:
        if cursor < start:
            out.append((cursor, start))
        if end is None:
            return _normalize(tuple(out))
        cursor = end
    out.append((cursor, None))
    return _normalize(tuple(out))


def _normalize(intervals: tuple[Interval, ...]) -> Intervals:
    cleaned: list[Interval] = []
    for start, end in sorted(intervals, key=lambda item: item[0]):
        if start < 0:
            raise ValueError("interval starts must be non-negative")
        if end is not None and end <= start:
            continue

        if not cleaned:
            cleaned.append((start, end))
            continue

        prev_start, prev_end = cleaned[-1]
        if prev_end is None:
            continue
        if start <= prev_end:
            cleaned[-1] = (prev_start, _max_end(prev_end, end))
        else:
            cleaned.append((start, end))
    return tuple(cleaned)


def _min_end(a: End, b: End) -> End:
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


def _max_end(a: End, b: End) -> End:
    if a is None or b is None:
        return None
    return max(a, b)


def _end_leq(a: End, b: End) -> bool:
    if b is None:
        return True
    if a is None:
        return False
    return a <= b


# ---------------------------------------------------------------------------
# Interval normal form -> Formula normal form
# ---------------------------------------------------------------------------


def _intervals_to_formula(s: Intervals) -> Formula:
    if not s:
        return bot()
    if s == _UNIVERSE:
        return _top()

    terms: list[Formula] = []
    for start, end in s:
        if end is None:
            terms.append(_tail_formula(start))
        elif start == 0:
            terms.append(box_power(bot(), end))
        else:
            terms.append(And(box_power(bot(), end), Not(box_power(bot(), start))))

    if not terms:
        return bot()
    if len(terms) == 1:
        return terms[0]
    return Or(*terms)


def _tail_formula(start: int) -> Formula:
    if start == 0:
        return _top()
    return Not(box_power(bot(), start))


def _top() -> Formula:
    return Not(bot())


def _json_key(f: Formula) -> str:
    return json.dumps(f.to_json(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
