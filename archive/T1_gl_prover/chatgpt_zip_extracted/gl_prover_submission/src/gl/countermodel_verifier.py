from __future__ import annotations

from typing import Any, Mapping

from .formula import Formula, ensure_formula


def verify_countermodel(formula: Formula | Mapping[str, Any], model: Mapping[str, Any]) -> bool:
    """Independent pure checker for GL countermodel JSON.

    Checks exactly the contract needed by the project:
    (a) the frame is transitive, (b) the frame is irreflexive, and
    (c) the displayed root refutes the supplied formula.

    This module intentionally evaluates Formula JSON dictionaries directly rather
    than calling the tableau or finite-search evaluators.
    """
    f = ensure_formula(formula).to_json()
    worlds = _worlds(model)
    rel = _rel(model)
    if not _rel_mentions_only_worlds(rel, worlds):
        return False
    if not is_irreflexive(worlds, rel):
        return False
    if not is_transitive(rel):
        return False
    root = int(model.get("refutes", {}).get("at", 0))
    if root not in worlds:
        return False
    return not _eval_json_formula(f, model, root)


def is_irreflexive(worlds: set[int], rel: set[tuple[int, int]]) -> bool:
    return all((w, w) not in rel for w in worlds) and all(a != b for a, b in rel)


def is_transitive(rel: set[tuple[int, int]]) -> bool:
    return all((a, c) in rel for a, b in rel for x, c in rel if b == x)


def _worlds(model: Mapping[str, Any]) -> set[int]:
    raw = model.get("worlds", [])
    if not isinstance(raw, list):
        raise ValueError("model['worlds'] must be a list")
    return {int(w) for w in raw}


def _rel(model: Mapping[str, Any]) -> set[tuple[int, int]]:
    raw = model.get("rel", [])
    if not isinstance(raw, list):
        raise ValueError("model['rel'] must be a list")
    out: set[tuple[int, int]] = set()
    for edge in raw:
        if not isinstance(edge, list | tuple) or len(edge) != 2:
            raise ValueError("each relation edge must be a pair")
        out.add((int(edge[0]), int(edge[1])))
    return out


def _rel_mentions_only_worlds(rel: set[tuple[int, int]], worlds: set[int]) -> bool:
    return all(a in worlds and b in worlds for a, b in rel)


def _valuation(model: Mapping[str, Any]) -> dict[str, set[int]]:
    raw = model.get("val", {})
    if not isinstance(raw, Mapping):
        raise ValueError("model['val'] must be an object")
    return {str(k): {int(w) for w in v} for k, v in raw.items()}


def _eval_json_formula(formula: Mapping[str, Any], model: Mapping[str, Any], world: int) -> bool:
    rel = _rel(model)
    val = _valuation(model)

    def ev(f: Mapping[str, Any], w: int) -> bool:
        t = f.get("type")
        if t == "bot":
            return False
        if t == "atom":
            name = f.get("name")
            if not isinstance(name, str):
                raise ValueError("atom requires string name")
            return w in val.get(name, set())
        if t == "not":
            return not ev(_arg(f), w)
        if t == "and":
            return all(ev(g, w) for g in _args(f))
        if t == "or":
            return any(ev(g, w) for g in _args(f))
        if t == "imp":
            return (not ev(_left(f), w)) or ev(_right(f), w)
        if t == "iff":
            return ev(_left(f), w) == ev(_right(f), w)
        if t == "box":
            return all(ev(_arg(f), v) for x, v in rel if x == w)
        raise ValueError(f"unknown formula type: {t!r}")

    return ev(formula, world)


def _arg(f: Mapping[str, Any]) -> Mapping[str, Any]:
    x = f.get("arg")
    if not isinstance(x, Mapping):
        raise ValueError("unary formula requires arg")
    return x


def _args(f: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    xs = f.get("args")
    if not isinstance(xs, list) or not all(isinstance(x, Mapping) for x in xs):
        raise ValueError("n-ary formula requires args")
    return xs


def _left(f: Mapping[str, Any]) -> Mapping[str, Any]:
    x = f.get("left")
    if not isinstance(x, Mapping):
        raise ValueError("binary formula requires left")
    return x


def _right(f: Mapping[str, Any]) -> Mapping[str, Any]:
    x = f.get("right")
    if not isinstance(x, Mapping):
        raise ValueError("binary formula requires right")
    return x


__all__ = ["verify_countermodel", "is_irreflexive", "is_transitive"]
