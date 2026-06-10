from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Literal

from .formula import Formula, ProofResult, atoms, ensure_formula, eval_formula, modal_depth

Signed = tuple[int, bool, Formula]
ExpansionKind = Literal["alpha", "beta", "modal", "none", "close"]


@dataclass
class Branch:
    signs: set[Signed] = field(default_factory=set)
    rel: set[tuple[int, int]] = field(default_factory=set)
    levels: dict[int, int] = field(default_factory=lambda: {0: 0})
    next_world: int = 1
    processed: set[Signed] = field(default_factory=set)
    trace: list[dict[str, Any]] = field(default_factory=list)

    def clone(self) -> "Branch":
        return Branch(
            signs=set(self.signs),
            rel=set(self.rel),
            levels=dict(self.levels),
            next_world=self.next_world,
            processed=set(self.processed),
            trace=list(self.trace),
        )

    def add(self, world: int, truth: bool, formula: Formula) -> bool:
        item = (world, truth, formula)
        if item in self.signs:
            return False
        self.signs.add(item)
        return True


def prove_gl(formula: Formula | dict[str, Any]) -> ProofResult:
    """Method A: signed, labelled GL tableau.

    The tableau attempts to satisfy F(formula) at root 0.  A saturated open branch
    is read as a finite transitive irreflexive Kripke countermodel.  If every
    branch closes, the returned certificate is a JSON-serialisable tableau tree.
    """
    f = ensure_formula(formula)
    root = Branch()
    root.add(0, False, f)
    limit = modal_depth(f)
    open_branch, cert = _expand(root, root_formula=f, depth_limit=limit)
    if open_branch is not None:
        model = branch_to_countermodel(open_branch, f)
        return ProofResult(status="refuted", certificate=None, countermodel=model)
    return ProofResult(status="proved", certificate=cert, countermodel=None)


def branch_to_countermodel(branch: Branch, formula: Formula) -> dict[str, Any]:
    worlds = sorted(branch.levels)
    rel = sorted(branch.rel)
    atom_names = sorted(atoms(formula) | {g.name for _, _, g in branch.signs if g.type == "atom" and g.name})
    val: dict[str, list[int]] = {}
    for name in atom_names:
        true_worlds = sorted(w for w, truth, g in branch.signs if truth and g.type == "atom" and g.name == name)
        val[name] = true_worlds
    model = {
        "worlds": worlds,
        "rel": [[a, b] for a, b in rel],
        "val": val,
        "refutes": {"formula": formula.to_json(), "at": 0},
        "checks": {
            "transitive": _is_transitive(set(rel), set(worlds)),
            "irreflexive": _is_irreflexive(set(rel), set(worlds)),
        },
    }
    # Construction invariant.  Keep this as an internal assertion rather than a
    # trusted verification path; tests call countermodel_verifier independently.
    assert not eval_formula(formula, model, 0), _debug_branch(branch)
    return model


def _expand(branch: Branch, *, root_formula: Formula, depth_limit: int) -> tuple[Branch | None, dict[str, Any]]:
    propagation_event = _propagate_boxes(branch)
    if propagation_event is not None:
        branch.trace.append(propagation_event)

    close = _closure_reason(branch)
    if close is not None:
        return None, _closed_cert(close, branch)

    alpha = _select(branch, kind="alpha")
    if alpha is not None:
        w, truth, formula = alpha
        child = branch.clone()
        child.processed.add(alpha)
        components = _alpha_components(truth, formula)
        for t, g in components:
            child.add(w, t, g)
        child.trace.append(
            {
                "rule": "alpha",
                "world": w,
                "sign": _sign_name(truth),
                "formula": formula.to_json(),
                "adds": [{"sign": _sign_name(t), "formula": g.to_json()} for t, g in components],
            }
        )
        open_branch, child_cert = _expand(child, root_formula=root_formula, depth_limit=depth_limit)
        return open_branch, {"rule": "alpha", "principal": _signed_json(alpha), "child": child_cert}

    beta = _select(branch, kind="beta")
    if beta is not None:
        w, truth, formula = beta
        alternatives = _beta_alternatives(truth, formula)
        if not alternatives:
            return None, _closed_cert({"type": "empty_beta", "principal": _signed_json(beta)}, branch)
        branch_certs: list[dict[str, Any]] = []
        for i, alt in enumerate(alternatives):
            child = branch.clone()
            child.processed.add(beta)
            for t, g in alt:
                child.add(w, t, g)
            child.trace.append(
                {
                    "rule": "beta",
                    "branch_index": i,
                    "world": w,
                    "sign": _sign_name(truth),
                    "formula": formula.to_json(),
                    "adds": [{"sign": _sign_name(t), "formula": g.to_json()} for t, g in alt],
                }
            )
            open_branch, child_cert = _expand(child, root_formula=root_formula, depth_limit=depth_limit)
            branch_certs.append(child_cert)
            if open_branch is not None:
                return open_branch, {
                    "rule": "beta",
                    "principal": _signed_json(beta),
                    "closed": False,
                    "open_branch_index": i,
                    "branches": branch_certs,
                }
        return None, {
            "rule": "beta",
            "principal": _signed_json(beta),
            "closed": True,
            "branches": branch_certs,
        }

    loop = _gl_loop_reason(branch)
    if loop is not None:
        return None, _closed_cert(loop, branch)

    modal = _select(branch, kind="modal")
    if modal is not None:
        w, truth, formula = modal
        assert not truth and formula.type == "box" and formula.arg is not None
        new_level = branch.levels[w] + 1
        if new_level > depth_limit:
            return None, _closed_cert(
                {
                    "type": "reverse_well_founded_depth_bound",
                    "principal": _signed_json(modal),
                    "world_level": branch.levels[w],
                    "attempted_successor_level": new_level,
                    "modal_depth_bound": depth_limit,
                },
                branch,
            )
        child = branch.clone()
        child.processed.add(modal)
        v = child.next_world
        child.next_world += 1
        child.levels[v] = new_level
        predecessors = {u for u, x in child.rel if x == w} | {w}
        for u in predecessors:
            child.rel.add((u, v))
        child.add(v, False, formula.arg)
        child.trace.append(
            {
                "rule": "gl_diamond_witness",
                "from": w,
                "to": v,
                "successor_level": new_level,
                "principal": _signed_json(modal),
                "adds": [{"world": v, "sign": "F", "formula": formula.arg.to_json()}],
                "frame_update": "added predecessor-closed edges to preserve transitivity; no reflexive edge added",
            }
        )
        open_branch, child_cert = _expand(child, root_formula=root_formula, depth_limit=depth_limit)
        return open_branch, {"rule": "gl_diamond_witness", "principal": _signed_json(modal), "child": child_cert}

    return branch, {
        "closed": False,
        "reason": "saturated_open_branch",
        "snapshot": _snapshot(branch),
    }


def _select(branch: Branch, *, kind: ExpansionKind) -> Signed | None:
    for item in sorted(branch.signs, key=_signed_sort_key):
        if item in branch.processed:
            continue
        w, truth, formula = item
        if _expansion_kind(truth, formula) == kind:
            return item
    return None


def _expansion_kind(truth: bool, f: Formula) -> ExpansionKind:
    t = f.type
    if t in {"atom", "bot"}:
        return "none"
    if t == "not":
        return "alpha"
    if t == "and":
        return "alpha" if truth else "beta"
    if t == "or":
        return "beta" if truth else "alpha"
    if t == "imp":
        return "beta" if truth else "alpha"
    if t == "iff":
        return "beta"
    if t == "box":
        return "none" if truth else "modal"
    raise ValueError(f"unknown formula type: {t!r}")


def _alpha_components(truth: bool, f: Formula) -> list[tuple[bool, Formula]]:
    t = f.type
    if t == "not":
        assert f.arg is not None
        return [(not truth, f.arg)]
    if t == "and" and truth:
        return [(True, a) for a in f.args]
    if t == "or" and not truth:
        return [(False, a) for a in f.args]
    if t == "imp" and not truth:
        assert f.left is not None and f.right is not None
        return [(True, f.left), (False, f.right)]
    raise ValueError(f"not an alpha formula: {truth=} {f=}")


def _beta_alternatives(truth: bool, f: Formula) -> list[list[tuple[bool, Formula]]]:
    t = f.type
    if t == "and" and not truth:
        return [[(False, a)] for a in f.args]
    if t == "or" and truth:
        return [[(True, a)] for a in f.args]
    if t == "imp" and truth:
        assert f.left is not None and f.right is not None
        return [[(False, f.left)], [(True, f.right)]]
    if t == "iff" and truth:
        assert f.left is not None and f.right is not None
        return [[(True, f.left), (True, f.right)], [(False, f.left), (False, f.right)]]
    if t == "iff" and not truth:
        assert f.left is not None and f.right is not None
        return [[(True, f.left), (False, f.right)], [(False, f.left), (True, f.right)]]
    raise ValueError(f"not a beta formula: {truth=} {f=}")


def _propagate_boxes(branch: Branch) -> dict[str, Any] | None:
    additions: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        true_boxes = [(w, f.arg) for w, truth, f in branch.signs if truth and f.type == "box" and f.arg is not None]
        for w, arg in sorted(true_boxes, key=lambda x: (x[0], _formula_sort_key(x[1]))):
            for x, v in sorted(branch.rel):
                if x == w and branch.add(v, True, arg):
                    changed = True
                    additions.append({"from": w, "to": v, "sign": "T", "formula": arg.to_json()})
    if additions:
        return {"rule": "box_propagation", "adds": additions}
    return None


def _closure_reason(branch: Branch) -> dict[str, Any] | None:
    by_world: dict[int, dict[Formula, set[bool]]] = {}
    for w, truth, formula in branch.signs:
        if truth and formula.type == "bot":
            return {"type": "truth_of_bottom", "world": w}
        by_world.setdefault(w, {}).setdefault(formula, set()).add(truth)
    for w in sorted(by_world):
        for formula, signs in sorted(by_world[w].items(), key=lambda item: _formula_sort_key(item[0])):
            if signs == {False, True}:
                return {"type": "signed_contradiction", "world": w, "formula": formula.to_json()}
    if not _is_irreflexive(branch.rel, set(branch.levels)):
        return {"type": "reflexive_edge"}
    if not _is_transitive(branch.rel, set(branch.levels)):
        return {"type": "non_transitive_edge"}
    return None


def _gl_loop_reason(branch: Branch) -> dict[str, Any] | None:
    """Detect a GL-forbidden self-similar eventuality on an ancestor chain.

    This is deliberately conservative: it only closes exact repeated signed
    world-types, and only when the lower world still has an unexpanded F□A.
    The separate modal-depth guard handles the remaining finite-height cases.
    """
    signatures = {w: _world_signature(branch, w) for w in branch.levels}
    for w in sorted(branch.levels, key=lambda x: branch.levels[x]):
        pending = [s for s in branch.signs if s[0] == w and s[1] is False and s[2].type == "box" and s not in branch.processed]
        if not pending:
            continue
        for a in sorted(_ancestors(branch, w), key=lambda x: branch.levels[x]):
            if branch.levels[a] < branch.levels[w] and signatures[a] == signatures[w]:
                return {
                    "type": "gl_loop_signature",
                    "ancestor": a,
                    "world": w,
                    "signature": [_signed_local_json(t, g) for t, g in sorted(signatures[w], key=lambda x: (_sign_name(x[0]), _formula_sort_key(x[1])))],
                    "pending_eventualities": [_signed_json(s) for s in pending],
                }
    return None


def _world_signature(branch: Branch, w: int) -> frozenset[tuple[bool, Formula]]:
    return frozenset((truth, formula) for x, truth, formula in branch.signs if x == w)


def _ancestors(branch: Branch, w: int) -> set[int]:
    return {u for u, v in branch.rel if v == w}


def _closed_cert(reason: dict[str, Any], branch: Branch) -> dict[str, Any]:
    return {
        "closed": True,
        "reason": reason,
        "snapshot": _snapshot(branch),
    }


def _snapshot(branch: Branch, *, max_signs: int = 40) -> dict[str, Any]:
    signs = sorted(branch.signs, key=_signed_sort_key)
    return {
        "worlds": sorted(branch.levels),
        "levels": {str(k): v for k, v in sorted(branch.levels.items())},
        "rel": [[a, b] for a, b in sorted(branch.rel)],
        "signs": [_signed_json(s) for s in signs[:max_signs]],
        "omitted_signs": max(0, len(signs) - max_signs),
        "checks": {
            "transitive": _is_transitive(branch.rel, set(branch.levels)),
            "irreflexive": _is_irreflexive(branch.rel, set(branch.levels)),
        },
    }


def _signed_json(s: Signed) -> dict[str, Any]:
    w, truth, f = s
    return {"world": w, "sign": _sign_name(truth), "formula": f.to_json()}


def _signed_local_json(truth: bool, f: Formula) -> dict[str, Any]:
    return {"sign": _sign_name(truth), "formula": f.to_json()}


def _sign_name(truth: bool) -> str:
    return "T" if truth else "F"


def _signed_sort_key(s: Signed) -> tuple[int, str, str]:
    w, truth, f = s
    return (w, _sign_name(truth), _formula_sort_key(f))


def _formula_sort_key(f: Formula) -> str:
    return json.dumps(f.to_json(), sort_keys=True, separators=(",", ":"))


def _is_irreflexive(rel: Iterable[tuple[int, int]], worlds: set[int]) -> bool:
    return all(a != b for a, b in rel) and all((w, w) not in set(rel) for w in worlds)


def _is_transitive(rel: Iterable[tuple[int, int]], worlds: set[int]) -> bool:
    r = set(rel)
    return all((a, c) in r for a, b in r for x, c in r if b == x)


def _debug_branch(branch: Branch) -> str:
    return json.dumps(_snapshot(branch, max_signs=200), ensure_ascii=False, sort_keys=True, indent=2)


__all__ = ["Branch", "branch_to_countermodel", "prove_gl"]
