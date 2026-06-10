"""
Independent verifier for Kripke countermodels.
Checks:
- worlds: list[int]
- rel: list[list[int,int]]  (edges)
- val: dict[str, list[int]]  atom -> worlds where true
- refutes: {"formula": json_formula, "at": root_world}
- checks: {"transitive": bool, "irreflexive": bool}  (expected True)

Verifies the model satisfies the frame conditions and root does not satisfy the formula.
Uses pure functions, no side effects.
"""

from __future__ import annotations

from typing import Dict, List, Any, Set, Tuple, Optional
from .formula import Formula, Atom, Not, And, Or, Imp, Iff, Box, from_json, modal_depth, get_atoms, pretty, bot


def _parse_kripke_json(km: Dict[str, Any]) -> Tuple[
    List[int], List[Tuple[int, int]], Dict[str, Set[int]], Formula, int, Dict[str, bool]
]:
    """Parse and basic validation of Kripke JSON."""
    worlds: List[int] = km.get("worlds", [])
    if not isinstance(worlds, list) or not all(isinstance(w, int) for w in worlds):
        raise ValueError("worlds must be list of int")
    if len(worlds) != len(set(worlds)):
        raise ValueError("worlds must be unique")
    worlds_set = set(worlds)

    rel_raw: List[List[int]] = km.get("rel", [])
    rel: List[Tuple[int, int]] = []
    for e in rel_raw:
        if not (isinstance(e, list) and len(e) == 2 and all(isinstance(x, int) for x in e)):
            raise ValueError("rel must be list of [int,int]")
        a, b = e
        if a not in worlds_set or b not in worlds_set:
            raise ValueError(f"rel edge {e} has unknown world")
        if a == b:
            raise ValueError(f"irreflexive violation in input rel: {e}")
        rel.append((a, b))

    val_raw: Dict[str, List[int]] = km.get("val", {})
    val: Dict[str, Set[int]] = {}
    for atom, wlist in val_raw.items():
        if not isinstance(atom, str):
            raise ValueError("val keys must be str")
        if not isinstance(wlist, list):
            raise ValueError("val values must be list of worlds")
        wset = set()
        for w in wlist:
            if w not in worlds_set:
                raise ValueError(f"val for {atom} has unknown world {w}")
            wset.add(w)
        val[atom] = wset

    refutes = km.get("refutes", {})
    if not isinstance(refutes, dict):
        raise ValueError("refutes must be dict")
    formula_json = refutes.get("formula")
    if formula_json is None:
        raise ValueError("refutes.formula missing")
    try:
        formula = from_json(formula_json)
    except Exception as ex:
        raise ValueError(f"bad formula in refutes: {ex}") from ex

    at = refutes.get("at", 0)
    if at not in worlds_set:
        raise ValueError(f"refutes.at={at} not in worlds")

    checks = km.get("checks", {})
    expected_trans = checks.get("transitive", True)
    expected_irref = checks.get("irreflexive", True)

    return worlds, rel, val, formula, at, {"transitive": expected_trans, "irreflexive": expected_irref}


def _compute_transitive_closure(worlds: List[int], rel: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """Floyd-Warshall style transitive closure for small graphs."""
    n = len(worlds)
    idx = {w: i for i, w in enumerate(worlds)}
    reach = [[False] * n for _ in range(n)]
    for a, b in rel:
        reach[idx[a]][idx[b]] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    closure: Set[Tuple[int, int]] = set()
    for i in range(n):
        for j in range(n):
            if reach[i][j]:
                closure.add((worlds[i], worlds[j]))
    return closure


def verify_countermodel(km: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify the countermodel JSON.
    Returns dict with 'valid': bool, 'reason': str or details, 'checked': {...}
    Raises on parse error.
    """
    worlds, rel, val, formula, root, expected = _parse_kripke_json(km)

    # 1. Check irreflexive (no self-loops in input, already raised if had)
    irreflexive = True  # enforced at parse for input edges; closure may introduce if cycle!
    # But we will check closure has no self

    # 2. Compute transitive closure and check irreflexive on closure (no cycles)
    closure = _compute_transitive_closure(worlds, rel)
    for w in worlds:
        if (w, w) in closure:
            return {
                "valid": False,
                "reason": f"cycle detected: world {w} reaches itself (not irreflexive after transitive closure)",
                "checked": {"transitive": True, "irreflexive": False},
            }

    # Check user expected
    if not expected["irreflexive"]:
        # if test expects false, but we don't support non-irref here
        pass

    # 3. Check transitive: the given rel's closure should satisfy that if aRb and bRc then aRc, but since we use closure for semantics, we always enforce transitive semantics.
    # For the model to be transitive frame, the accessibility relation used for semantics must be transitive.
    # We will use closure for all box evaluations.

    # 4. Now evaluate formula at all worlds under the model (using closure for R)
    # Build full truth assignment for all subformulas? Or just evaluate the target formula.
    # Since may have bot, treat 'bot' as always False, 'top' always True.

    def satisfies(w: int, f: Formula, memo: Optional[Dict[Tuple[int, Formula], bool]] = None) -> bool:
        if memo is None:
            memo = {}
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
            res = not satisfies(w, f.arg, memo)
        elif isinstance(f, And):
            res = all(satisfies(w, a, memo) for a in f.args)
        elif isinstance(f, Or):
            res = any(satisfies(w, a, memo) for a in f.args)
        elif isinstance(f, Imp):
            res = (not satisfies(w, f.left, memo)) or satisfies(w, f.right, memo)
        elif isinstance(f, Iff):
            l = satisfies(w, f.left, memo)
            r = satisfies(w, f.right, memo)
            res = l == r
        elif isinstance(f, Box):
            # true iff ALL v s.t. w R v (in closure) satisfy arg
            res = True
            for v in worlds:
                if (w, v) in closure:
                    if not satisfies(v, f.arg, memo):
                        res = False
                        break
        else:
            raise TypeError(f"Unknown formula {f}")
        memo[key] = res
        return res

    root_satisfies = satisfies(root, formula)
    refutes_ok = not root_satisfies

    result = {
        "valid": refutes_ok and irreflexive,
        "reason": "OK" if refutes_ok else f"root world {root} satisfies the formula (should refute)",
        "checked": {
            "transitive": True,  # we used closure, so semantics is transitive
            "irreflexive": all((w, w) not in closure for w in worlds),
            "num_worlds": len(worlds),
            "num_edges": len(rel),
            "formula_pretty": pretty(formula),
            "root_satisfies_formula": root_satisfies,
        },
    }
    return result


if __name__ == "__main__":
    # Test with the n=0 strict case: 2-chain x=0 -> t=1 , refutes Con0 → Con1
    from .formula import con_n, make_con_strict, to_json
    worlds = [0, 1]
    rel = [[0, 1]]
    val = {}  # no atoms needed
    formula = make_con_strict(0)  # Con0 → Con1
    km = {
        "worlds": worlds,
        "rel": rel,
        "val": val,
        "refutes": {"formula": to_json(formula), "at": 0},
        "checks": {"transitive": True, "irreflexive": True},
    }
    res = verify_countermodel(km)
    print(res)
    assert res["valid"], "KAT n=0 should validate"
    print("Verifier self-test passed for Con0 strictness countermodel.")
