"""Letterless normal-form reducer for GL.

The reducer is intentionally independent of any GL prover.  Correctness is
checked in tests by asking an external prover to prove
    GL |- input <-> letterless_normal_form(input).

Semantic idea used here: in the closed fragment of GL, truth on the canonical
rank frame depends only on the natural-number rank of a world.  Each generator
B_n = box_power(bot(), n) denotes the initial segment {0, ..., n-1}; B_0 is the
empty set, and Not(bot()) denotes all ranks.  Boolean operations are exact set
operations on finite unions of half-open intervals, and Box(S) is the initial
segment whose length is one more than the first rank not in S (or all ranks if
S is universal).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, TypeAlias

from gl.formula import And, Formula, Not, Or, atoms, bot, box_power

End: TypeAlias = int | None
Interval: TypeAlias = tuple[int, End]
Intervals: TypeAlias = tuple[Interval, ...]

_EMPTY: Intervals = ()
_UNIVERSE: Intervals = ((0, None),)
_MISSING = object()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_letterless(F: Formula) -> bool:
    """Return True iff F contains no atom node."""

    try:
        return len(atoms(F)) == 0
    except Exception:
        # Keep the reducer usable if a local Formula implementation has a
        # partial atoms() helper.  The fallback walks Formula/to_json structure.
        return not _contains_atom(F)


def letterless_normal_form(F: Formula) -> Formula:
    """Return a canonical Boolean combination of box_power(bot(), n).

    The function does not import or call gl.tableau/prove_gl or any other GL
    decision procedure.  It raises ValueError on formulas with propositional
    atoms.
    """

    if not is_letterless(F):
        raise ValueError("letterless_normal_form expects a formula with no atoms")
    return _intervals_to_formula(_eval(F))


def nf_equiv(F1: Formula, F2: Formula) -> bool:
    """Decide GL-equivalence of two letterless formulas by canonical NF equality."""

    if not is_letterless(F1) or not is_letterless(F2):
        raise ValueError("nf_equiv expects two formulas with no atoms")
    nf1 = letterless_normal_form(F1)
    nf2 = letterless_normal_form(F2)
    return _json_key(nf1) == _json_key(nf2)


# ---------------------------------------------------------------------------
# Closed-fragment interval semantics
# ---------------------------------------------------------------------------


def _eval(node: Any) -> Intervals:
    kind, children = _view(node)

    if kind == "bot":
        return _EMPTY
    if kind == "top":
        return _UNIVERSE
    if kind == "atom":
        raise ValueError("letterless_normal_form expects a formula with no atoms")

    if kind == "not":
        _require_arity(kind, children, 1)
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
        _require_arity(kind, children, 2)
        left, right = children
        return _union(_complement(_eval(left)), _eval(right))

    if kind == "iff":
        _require_arity(kind, children, 2)
        left = _eval(children[0])
        right = _eval(children[1])
        return _union(_intersection(left, right), _intersection(_complement(left), _complement(right)))

    if kind == "box":
        _require_arity(kind, children, 1)
        return _box(_eval(children[0]))

    raise TypeError(f"unsupported formula node type: {kind!r}")


def _box(s: Intervals) -> Intervals:
    """Modal box on rank sets.

    If g is the first natural number not in s, Box(s) is {0, ..., g}; if s is
    all of N, Box(s) is all of N.  This matches □φ at rank n being true exactly
    when φ holds at every lower rank.
    """

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


# ---------------------------------------------------------------------------
# Formula/to_json structural reader
# ---------------------------------------------------------------------------


def _contains_atom(node: Any) -> bool:
    kind, children = _view(node)
    return kind == "atom" or any(_contains_atom(child) for child in children)


def _view(node: Any) -> tuple[str, tuple[Any, ...]]:
    source = _mapping_view(node)
    if source is None:
        source = node

    kind = _normal_kind(_field(source, "type", "kind", "op", "operator", "tag"))
    if kind is None:
        kind = _normal_kind(type(node).__name__)
    if kind is None:
        raise TypeError(f"cannot identify formula node type for {node!r}")

    if kind in {"bot", "top", "atom"}:
        return kind, ()
    if kind in {"not", "box"}:
        return kind, (_unary_child(source),)
    if kind in {"and", "or"}:
        return kind, _nary_children(source)
    if kind in {"imp", "iff"}:
        return kind, _binary_children(source)
    raise TypeError(f"unsupported formula node type: {kind!r}")


def _mapping_view(node: Any) -> Mapping[str, Any] | None:
    if isinstance(node, Mapping):
        return node
    to_json = getattr(node, "to_json", None)
    if callable(to_json):
        data = to_json()
        if isinstance(data, Mapping):
            return data
    return None


def _field(source: Any, *names: str) -> Any:
    if isinstance(source, Mapping):
        for name in names:
            if name in source:
                return source[name]
    else:
        for name in names:
            if hasattr(source, name):
                return getattr(source, name)
    return _MISSING


def _unary_child(source: Any) -> Any:
    direct = _field(source, "arg", "body", "formula", "operand", "child")
    if direct is not _MISSING:
        return direct
    for key in ("args", "children", "operands"):
        seq = _as_sequence(_field(source, key))
        if seq is not None and len(seq) == 1:
            return seq[0]
    raise TypeError(f"cannot extract unary child from {source!r}")


def _binary_children(source: Any) -> tuple[Any, Any]:
    left = _field(source, "left", "lhs")
    right = _field(source, "right", "rhs")
    if left is not _MISSING and right is not _MISSING:
        return left, right

    for key in ("args", "children", "operands"):
        seq = _as_sequence(_field(source, key))
        if seq is not None and len(seq) == 2:
            return seq[0], seq[1]
    raise TypeError(f"cannot extract binary children from {source!r}")


def _nary_children(source: Any) -> tuple[Any, ...]:
    for key in ("args", "children", "operands"):
        seq = _as_sequence(_field(source, key))
        if seq is not None:
            return tuple(seq)

    left = _field(source, "left", "lhs")
    right = _field(source, "right", "rhs")
    if left is not _MISSING and right is not _MISSING:
        return left, right
    raise TypeError(f"cannot extract n-ary children from {source!r}")


def _as_sequence(value: Any) -> tuple[Any, ...] | None:
    if value is _MISSING or value is None:
        return None
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(value)
    return None


def _normal_kind(raw: Any) -> str | None:
    if raw is _MISSING or raw is None:
        return None
    if hasattr(raw, "value"):
        raw = raw.value
    elif hasattr(raw, "name"):
        raw = raw.name

    text = str(raw).strip().lower().split(".")[-1]
    aliases = {
        "bot": "bot",
        "bottom": "bot",
        "false": "bot",
        "falsum": "bot",
        "⊥": "bot",
        "top": "top",
        "true": "top",
        "verum": "top",
        "⊤": "top",
        "atom": "atom",
        "var": "atom",
        "variable": "atom",
        "prop": "atom",
        "proposition": "atom",
        "not": "not",
        "neg": "not",
        "negation": "not",
        "¬": "not",
        "~": "not",
        "and": "and",
        "conj": "and",
        "conjunction": "and",
        "∧": "and",
        "&": "and",
        "or": "or",
        "disj": "or",
        "disjunction": "or",
        "∨": "or",
        "|": "or",
        "imp": "imp",
        "impl": "imp",
        "implies": "imp",
        "conditional": "imp",
        "->": "imp",
        "→": "imp",
        "iff": "iff",
        "equiv": "iff",
        "equivalence": "iff",
        "biconditional": "iff",
        "<->": "iff",
        "↔": "iff",
        "box": "box",
        "necessary": "box",
        "necessity": "box",
        "modal": "box",
        "□": "box",
    }
    return aliases.get(text)


def _require_arity(kind: str, children: tuple[Any, ...], expected: int) -> None:
    if len(children) != expected:
        raise TypeError(f"{kind!r} expects {expected} child/children, got {len(children)}")


def _json_key(f: Formula) -> str:
    to_json = getattr(f, "to_json", None)
    if callable(to_json):
        data = to_json()
        try:
            return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        except TypeError:
            return repr(data)
    return repr(f)
