from __future__ import annotations

import itertools
from functools import lru_cache
from typing import Any, Mapping

from .formula import Formula, ProofResult, atoms, ensure_formula, modal_depth, modal_subformulas


def prove_gl(formula: Formula | Mapping[str, Any]) -> ProofResult:
    """Method B: finite rooted Kripke-model exhaustion for GL.

    A finite GL frame is represented as a finite transitive irreflexive relation.
    The search enumerates rooted frames in increasing world count.  World count is
    bounded by the modal-subformula filtration bound used here; chain height is
    bounded by the input formula's modal depth.
    """
    f = ensure_formula(formula)
    atom_names = tuple(sorted(atoms(f)))
    height_bound = modal_depth(f)
    world_bound = _default_world_bound(f)
    frames_checked = 0
    valuations_checked = 0

    for n in range(1, world_bound + 1):
        for rel in _frames(n, height_bound):
            frames_checked += 1
            succ = _succ_map(n, rel)
            for val in _valuations(atom_names, n):
                valuations_checked += 1
                if not _eval(f, 0, succ, val, {}):
                    model = _model_json(f, n, rel, val)
                    return ProofResult(status="refuted", certificate=None, countermodel=model)

    return ProofResult(
        status="proved",
        certificate={
            "method": "finite_kripke_exhaustion",
            "closed_under": "finite transitive irreflexive rooted frames",
            "world_bound": world_bound,
            "height_bound": height_bound,
            "atoms": list(atom_names),
            "frames_checked": frames_checked,
            "valuations_checked": valuations_checked,
        },
        countermodel=None,
    )


def _default_world_bound(f: Formula) -> int:
    # In the finite-model/filtration reading, distinct modal subformulas are the
    # only reason to add new witness worlds.  The root contributes the +1.
    return max(1, len(modal_subformulas(f)) + 1)


@lru_cache(maxsize=None)
def _frames(n: int, height_bound: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    if n <= 0:
        return tuple()
    if n == 1:
        return (tuple(),)
    # Topological normal form: root is 0; every other world is reachable from 0,
    # hence transitivity forces 0 R i for all i > 0.
    fixed = {(0, j) for j in range(1, n)}
    optional = [(i, j) for i in range(1, n) for j in range(i + 1, n)]
    out: list[tuple[tuple[int, int], ...]] = []
    for mask in range(1 << len(optional)):
        rel = set(fixed)
        for bit, edge in enumerate(optional):
            if mask & (1 << bit):
                rel.add(edge)
        if _is_transitive(rel) and _height(n, rel) <= height_bound:
            out.append(tuple(sorted(rel)))
    out.sort(key=lambda r: (len(r), r))
    return tuple(out)


def _is_transitive(rel: set[tuple[int, int]]) -> bool:
    return all((a, c) in rel for a, b in rel for x, c in rel if b == x)


def _height(n: int, rel: set[tuple[int, int]]) -> int:
    succ = {w: [v for a, v in rel if a == w] for w in range(n)}

    @lru_cache(maxsize=None)
    def h(w: int) -> int:
        if not succ[w]:
            return 0
        return 1 + max(h(v) for v in succ[w])

    return max(h(w) for w in range(n))


def _succ_map(n: int, rel: tuple[tuple[int, int], ...]) -> dict[int, tuple[int, ...]]:
    return {w: tuple(v for a, v in rel if a == w) for w in range(n)}


def _valuations(atom_names: tuple[str, ...], n: int) -> Iterable[dict[str, frozenset[int]]]:
    if not atom_names:
        yield {}
        return
    total_bits = len(atom_names) * n
    for mask in range(1 << total_bits):
        val: dict[str, frozenset[int]] = {}
        for ai, name in enumerate(atom_names):
            worlds = [w for w in range(n) if mask & (1 << (ai * n + w))]
            val[name] = frozenset(worlds)
        yield val


def _eval(
    f: Formula,
    world: int,
    succ: dict[int, tuple[int, ...]],
    val: dict[str, frozenset[int]],
    memo: dict[tuple[Formula, int], bool],
) -> bool:
    key = (f, world)
    if key in memo:
        return memo[key]
    t = f.type
    if t == "bot":
        ans = False
    elif t == "atom":
        assert f.name is not None
        ans = world in val.get(f.name, frozenset())
    elif t == "not":
        assert f.arg is not None
        ans = not _eval(f.arg, world, succ, val, memo)
    elif t == "and":
        ans = all(_eval(a, world, succ, val, memo) for a in f.args)
    elif t == "or":
        ans = any(_eval(a, world, succ, val, memo) for a in f.args)
    elif t == "imp":
        assert f.left is not None and f.right is not None
        ans = (not _eval(f.left, world, succ, val, memo)) or _eval(f.right, world, succ, val, memo)
    elif t == "iff":
        assert f.left is not None and f.right is not None
        ans = _eval(f.left, world, succ, val, memo) == _eval(f.right, world, succ, val, memo)
    elif t == "box":
        assert f.arg is not None
        ans = all(_eval(f.arg, v, succ, val, memo) for v in succ[world])
    else:
        raise ValueError(f"unknown formula type: {t!r}")
    memo[key] = ans
    return ans


def _model_json(
    formula: Formula,
    n: int,
    rel: tuple[tuple[int, int], ...],
    val: dict[str, frozenset[int]],
) -> dict[str, Any]:
    return {
        "worlds": list(range(n)),
        "rel": [[a, b] for a, b in rel],
        "val": {name: sorted(worlds) for name, worlds in val.items()},
        "refutes": {"formula": formula.to_json(), "at": 0},
        "checks": {"transitive": _is_transitive(set(rel)), "irreflexive": all(a != b for a, b in rel)},
    }


def enumerate_finite_gl_frames(
    num_worlds: int,
    *,
    height_bound: int | None = None,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Enumerate all rooted finite GL frames on `num_worlds` worlds.

    Each returned frame is a sorted tuple of ``(source, target)`` edges
    representing the transitive irreflexive accessibility relation. World 0
    is the root and must reach every other world (transitivity then forces
    ``0 R i`` for all ``i > 0``); transitivity is enforced at generation
    time, not by post-hoc filtering. ``height_bound`` defaults to
    ``max(0, num_worlds - 1)`` which imposes no extra restriction beyond
    what ``num_worlds`` already implies.

    The result is cached via the underlying private enumerator, so repeated
    calls with the same arguments return the same tuple instance.
    """
    if num_worlds < 0:
        raise ValueError("num_worlds must be non-negative")
    bound = height_bound if height_bound is not None else max(0, num_worlds - 1)
    if bound < 0:
        raise ValueError("height_bound must be non-negative")
    return _frames(num_worlds, bound)


__all__ = ["prove_gl", "enumerate_finite_gl_frames"]
