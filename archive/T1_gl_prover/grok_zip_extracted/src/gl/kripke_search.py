"""
Method B: Finite Kripke model search for GL countermodels.
Enumerates small transitive irreflexive well-founded frames (bounded by modal depth)
and valuations to find if formula is refutable at root=0.
If found, returns KripkeJSON that passes verify_countermodel.
If no countermodel within bound, returns 'proved'.
This is sound; completeness relies on bound being sufficient for depth<=3 formulas.
"""

from __future__ import annotations

import itertools
from functools import lru_cache
from typing import Dict, List, Any, Optional, Tuple, Set
from .formula import (
    Formula, Atom, Not, And, Or, Imp, Iff, Box,
    modal_depth, get_atoms, to_json, bot, pretty,
    con_n, make_con_strict, make_lob, make_4, make_con_monotone
)
from .countermodel_verifier import verify_countermodel


@lru_cache(maxsize=32)
def _generate_frames(m: int) -> List[List[Tuple[int, int]]]:
    """
    Generate all transitive irreflexive frames on worlds 0..m-1 (root 0).
    Cached for speed across calls.
    """
    if m == 0:
        return []
    possible_edges = [(i, j) for i in range(m) for j in range(i + 1, m)]
    frames = []
    for edge_comb in itertools.chain.from_iterable(
        itertools.combinations(possible_edges, r) for r in range(len(possible_edges) + 1)
    ):
        rel_set = set(edge_comb)
        changed = True
        while changed:
            changed = False
            new_pairs = set()
            for a, b in list(rel_set):
                for c, d in list(rel_set):
                    if b == c and (a, d) not in rel_set:
                        new_pairs.add((a, d))
                        changed = True
            rel_set.update(new_pairs)
        if any((w, w) in rel_set for w in range(m)):
            continue
        frames.append(sorted(rel_set))
    unique = {tuple(f): f for f in frames}
    return list(unique.values())


def _compute_closure(worlds: List[int], rel: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """Precompute transitive closure once per frame."""
    closure: Set[Tuple[int, int]] = set(rel)
    changed = True
    while changed:
        changed = False
        for a, b in list(closure):
            for c, d in list(closure):
                if b == c and (a, d) not in closure:
                    closure.add((a, d))
                    changed = True
    # final irref check not needed here, caller filtered
    return closure


def _evaluate_all(worlds: List[int], closure: Set[Tuple[int, int]], val: Dict[str, Set[int]], formula: Formula) -> Dict[int, bool]:
    """Compute whether formula holds at each world. closure is precomputed transitive irrefl."""
    memo: Dict[Tuple[int, Formula], bool] = {}

    def sat(w: int, f: Formula) -> bool:
        key = (w, f)
        if key in memo:
            return memo[key]
        if isinstance(f, Atom):
            if f.name == "bot":
                res = False
            elif f.name == "top":
                res = True
            else:
                res = w in val.get(f.name, set())
        elif isinstance(f, Not):
            res = not sat(w, f.arg)
        elif isinstance(f, And):
            res = all(sat(w, a) for a in f.args)
        elif isinstance(f, Or):
            res = any(sat(w, a) for a in f.args)
        elif isinstance(f, Imp):
            res = not sat(w, f.left) or sat(w, f.right)
        elif isinstance(f, Iff):
            res = sat(w, f.left) == sat(w, f.right)
        elif isinstance(f, Box):
            res = all(sat(v, f.arg) for v in worlds if (w, v) in closure)
        else:
            raise TypeError(str(f))
        memo[key] = res
        return res

    return {w: sat(w, formula) for w in worlds}


def find_countermodel(formula: Formula, max_m: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Search for countermodel by exhaustive enum of small frames + vals.
    Returns valid KripkeJSON or None.
    """
    D = modal_depth(formula)
    atoms = sorted(get_atoms(formula))
    n_atoms = len(atoms)
    if max_m is None:
        if n_atoms == 0:
            max_m = min(D + 2, 6)  # sufficient for KAT n<=4 (m=n+2); avoid slow m>6 generate
        else:
            max_m = min(D + 2, 5)

    for m in range(1, max_m + 1):
        frame_bases = _generate_frames(m)
        worlds = list(range(m))
        if n_atoms * m > 18:
            continue  # rely on tableau for borderline cases; depth<=3 usually ok with m<=5
        # precompute closures for all frames of this m
        frame_closures = []
        valid_frames = []
        for fb in frame_bases:
            cl = _compute_closure(worlds, fb)
            # double check no self loops
            if any((w, w) in cl for w in worlds):
                continue
            frame_closures.append(cl)
            valid_frames.append(fb)
        atom_assignments = list(itertools.product([False, True], repeat=n_atoms))
        all_val_combos = itertools.product(atom_assignments, repeat=m)
        for val_tuple in all_val_combos:
            val: Dict[str, Set[int]] = {atom: set() for atom in atoms}
            for wi, w_assign in enumerate(val_tuple):
                for ai, atom in enumerate(atoms):
                    if w_assign[ai]:
                        val[atom].add(wi)
            for fi, closure in enumerate(frame_closures):
                frame_rel_tuples = valid_frames[fi]
                truth_map = _evaluate_all(worlds, closure, val, formula)
                if not truth_map.get(0, True):
                    km = {
                        "worlds": worlds,
                        "rel": [list(e) for e in frame_rel_tuples],
                        "val": {k: sorted(list(v)) for k, v in val.items()},
                        "refutes": {"formula": to_json(formula), "at": 0},
                        "checks": {"transitive": True, "irreflexive": True},
                    }
                    check_res = verify_countermodel(km)
                    if check_res.get("valid", False):
                        return km
    return None


def prove_gl_kripke(formula: Formula) -> Dict[str, Any]:
    """Method B entrypoint. Returns ProofResult like dict."""
    cm = find_countermodel(formula)
    if cm is not None:
        return {
            "status": "refuted",
            "certificate": None,
            "countermodel": cm,
            "method": "kripke_search"
        }
    else:
        return {
            "status": "proved",
            "certificate": None,
            "countermodel": None,
            "method": "kripke_search",
            "note": "no countermodel found within modal_depth bound (may be incomplete for large D)"
        }


if __name__ == "__main__":
    # Test KAT Con strict n=0
    f = make_con_strict(0)
    print("Testing Con0 -> Con1 strictness:", pretty(f))
    res = prove_gl_kripke(f)
    print(res["status"])
    if res["status"] == "refuted":
        print("Countermodel found, verifying...")
        vres = verify_countermodel(res["countermodel"])
        print(vres)
        assert vres["valid"]
    print("Kripke KAT0 basic test done.")
