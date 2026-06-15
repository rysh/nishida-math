"""
WP6 E-C1: finite Kripke-style fixed-point models for a transparent truth predicate.

This file is intentionally self-contained. It implements two finite constructions:

1. SK / paracomplete construction:
   - admissible states are consistent extension / anti-extension pairs (no overlaps)
   - order is inclusion in both coordinates
   - bottom is (empty, empty)
   - the finite least fixed point leaves the liar and truth-teller gappy (n)

2. LP / paraconsistent construction:
   - admissible states are complete extension / anti-extension pairs (no gaps)
   - order is reverse inclusion in both coordinates; b=(true,false) is the bottom
     element in the resulting precision order
   - bottom is (all codes, all codes)
   - the finite least fixed point gives the liar and truth-teller value b

The constructions use the same De Morgan/FDE pair semantics for connectives.
The difference is in the admissible state space, bottom element, and order.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
import json
from typing import Any, Iterable, Iterator, Literal, Mapping, Sequence

Formula = dict[str, Any]
Scheme = Literal["sk", "lp"]

# Pair value: (has_truth, has_falsity)
Value = tuple[bool, bool]
T_VAL: Value = (True, False)
F_VAL: Value = (False, True)
B_VAL: Value = (True, True)
N_VAL: Value = (False, False)

VALUE_TO_NAME: dict[Value, str] = {
    T_VAL: "t",
    F_VAL: "f",
    B_VAL: "b",
    N_VAL: "n",
}
NAME_TO_VALUE: dict[str, Value] = {v: k for k, v in VALUE_TO_NAME.items()}

BASE_ATOMS: dict[str, Value] = {
    "p": T_VAL,
    "q": F_VAL,
}


@dataclass(frozen=True)
class State:
    """Extension and anti-extension of the truth predicate over finite sentence codes."""

    plus: frozenset[str]
    minus: frozenset[str]

    def value_of_code(self, code: str) -> Value:
        return (code in self.plus, code in self.minus)

    def as_sorted_dict(self) -> dict[str, list[str]]:
        return {"E_plus": sorted(self.plus), "E_minus": sorted(self.minus)}


# ---------------------------------------------------------------------------
# Formula constructors. These use the repository's Formula JSON plus one node:
#   {"type": "T", "arg": "some_explicit_code"}
# ---------------------------------------------------------------------------


def Atom(name: str) -> Formula:
    return {"type": "atom", "name": name}


def Not(arg: Formula) -> Formula:
    return {"type": "not", "arg": arg}


def And(*args: Formula) -> Formula:
    return {"type": "and", "args": list(args)}


def Or(*args: Formula) -> Formula:
    return {"type": "or", "args": list(args)}


def T(code: str) -> Formula:
    return {"type": "T", "arg": code}


def canonical_formula(formula: Formula) -> str:
    """Stable JSON representation used for de-duplicating generated formulae."""
    return json.dumps(formula, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Finite code table.  The self-reference is explicit by table lookup:
#   code "liar" maps to formula ¬T("liar").
# No Goedel numbering is used.
# ---------------------------------------------------------------------------


def build_base_fragment() -> dict[str, Formula]:
    p = Atom("p")
    q = Atom("q")
    tau = T("truthteller")
    return {
        "p": p,
        "q": q,
        "p_or_q": Or(p, q),
        "T_p": T("p"),
        "T_q": T("q"),
        "truthteller": tau,
    }


def build_full_fragment() -> dict[str, Formula]:
    table = build_base_fragment()
    p = Atom("p")
    liar = Not(T("liar"))
    not_liar = Not(liar)
    table.update(
        {
            "liar": liar,
            "liar_and_not_liar": And(liar, not_liar),
            "liar_or_p": Or(liar, p),
        }
    )
    return table


# ---------------------------------------------------------------------------
# Truth functions: FDE pair semantics.  SK is the no-gluts subcase; LP is the
# no-gaps subcase.  LP designated values are t and b.
# ---------------------------------------------------------------------------


def v_not(v: Value) -> Value:
    return (v[1], v[0])


def v_and(values: Sequence[Value]) -> Value:
    if not values:
        return T_VAL
    return (all(v[0] for v in values), any(v[1] for v in values))


def v_or(values: Sequence[Value]) -> Value:
    if not values:
        return F_VAL
    return (any(v[0] for v in values), all(v[1] for v in values))


def value_name(v: Value) -> str:
    return VALUE_TO_NAME[v]


def designated_lp(v: Value) -> bool:
    return v in {T_VAL, B_VAL}


def eval_formula(formula: Formula, state: State, code_table: Mapping[str, Formula], base_atoms: Mapping[str, Value]) -> Value:
    typ = formula["type"]
    if typ == "atom":
        name = formula["name"]
        if name not in base_atoms:
            raise KeyError(f"No base value for atom {name!r}")
        return base_atoms[name]
    if typ == "not":
        return v_not(eval_formula(formula["arg"], state, code_table, base_atoms))
    if typ == "and":
        return v_and([eval_formula(arg, state, code_table, base_atoms) for arg in formula["args"]])
    if typ == "or":
        return v_or([eval_formula(arg, state, code_table, base_atoms) for arg in formula["args"]])
    if typ == "T":
        code = formula["arg"]
        if code not in code_table:
            raise KeyError(f"Truth predicate refers to unknown code {code!r}")
        return state.value_of_code(code)
    raise ValueError(f"Unsupported formula type {typ!r}")


def gamma(state: State, code_table: Mapping[str, Formula], base_atoms: Mapping[str, Value]) -> State:
    plus: set[str] = set()
    minus: set[str] = set()
    for code, formula in code_table.items():
        value = eval_formula(formula, state, code_table, base_atoms)
        if value[0]:
            plus.add(code)
        if value[1]:
            minus.add(code)
    return State(frozenset(plus), frozenset(minus))


# ---------------------------------------------------------------------------
# State-space, orders, fixed points, and finite certificates.
# ---------------------------------------------------------------------------


def codes_of(code_table: Mapping[str, Formula]) -> tuple[str, ...]:
    return tuple(sorted(code_table.keys()))


def is_valid_state(state: State, codes: Sequence[str], scheme: Scheme) -> bool:
    universe = set(codes)
    if not state.plus <= universe or not state.minus <= universe:
        return False
    if scheme == "sk":
        return state.plus.isdisjoint(state.minus)
    if scheme == "lp":
        return state.plus | state.minus == universe
    raise ValueError(scheme)


def bottom_state(codes: Sequence[str], scheme: Scheme) -> State:
    universe = frozenset(codes)
    if scheme == "sk":
        return State(frozenset(), frozenset())
    if scheme == "lp":
        return State(universe, universe)
    raise ValueError(scheme)


def leq_state(left: State, right: State, scheme: Scheme) -> bool:
    """Order used for least-fixed-point claims."""
    if scheme == "sk":
        return left.plus <= right.plus and left.minus <= right.minus
    if scheme == "lp":
        # LP precision order: b is bottom; moving upward removes surplus truth/falsity.
        return left.plus >= right.plus and left.minus >= right.minus
    raise ValueError(scheme)


def iter_states(codes: Sequence[str], scheme: Scheme) -> Iterator[State]:
    """Enumerate all admissible states: 3^n for SK and 3^n for LP."""
    if scheme == "sk":
        statuses = [N_VAL, T_VAL, F_VAL]
    elif scheme == "lp":
        statuses = [B_VAL, T_VAL, F_VAL]
    else:
        raise ValueError(scheme)
    for vals in product(statuses, repeat=len(codes)):
        plus = {code for code, val in zip(codes, vals) if val[0]}
        minus = {code for code, val in zip(codes, vals) if val[1]}
        yield State(frozenset(plus), frozenset(minus))


def covers_above(state: State, codes: Sequence[str], scheme: Scheme) -> Iterator[State]:
    """Immediate one-coordinate successors in the finite order."""
    for code in codes:
        current = state.value_of_code(code)
        if scheme == "sk" and current == N_VAL:
            yield set_code_value(state, code, T_VAL)
            yield set_code_value(state, code, F_VAL)
        elif scheme == "lp" and current == B_VAL:
            yield set_code_value(state, code, T_VAL)
            yield set_code_value(state, code, F_VAL)


def set_code_value(state: State, code: str, value: Value) -> State:
    plus = set(state.plus)
    minus = set(state.minus)
    if value[0]:
        plus.add(code)
    else:
        plus.discard(code)
    if value[1]:
        minus.add(code)
    else:
        minus.discard(code)
    return State(frozenset(plus), frozenset(minus))


def iterate_to_fixed_point(code_table: Mapping[str, Formula], scheme: Scheme, base_atoms: Mapping[str, Value]) -> tuple[State, list[State]]:
    codes = codes_of(code_table)
    state = bottom_state(codes, scheme)
    trace = [state]
    # On a finite 3^n lattice, monotone iteration from bottom reaches a fixed point
    # within the height bound n+1 for these product orders. Use a larger guard for diagnostics.
    max_steps = 3 * len(codes) + 10
    for _ in range(max_steps):
        nxt = gamma(state, code_table, base_atoms)
        trace.append(nxt)
        if nxt == state:
            return state, trace
        state = nxt
    raise RuntimeError(f"No fixed point reached within guard for scheme={scheme}")


def enumerate_fixed_points(code_table: Mapping[str, Formula], scheme: Scheme, base_atoms: Mapping[str, Value]) -> list[State]:
    codes = codes_of(code_table)
    out: list[State] = []
    for state in iter_states(codes, scheme):
        if gamma(state, code_table, base_atoms) == state:
            out.append(state)
    return out


def verify_monotone_by_covers(code_table: Mapping[str, Formula], scheme: Scheme, base_atoms: Mapping[str, Value]) -> dict[str, Any]:
    """Finite all-edge monotonicity check over the admissible 3^n state space."""
    codes = codes_of(code_table)
    states_checked = 0
    cover_edges_checked = 0
    failures: list[dict[str, Any]] = []
    for state in iter_states(codes, scheme):
        states_checked += 1
        g_state = gamma(state, code_table, base_atoms)
        if not is_valid_state(g_state, codes, scheme):
            failures.append({"kind": "validity", "state": state.as_sorted_dict(), "gamma": g_state.as_sorted_dict()})
            break
        for above in covers_above(state, codes, scheme):
            cover_edges_checked += 1
            g_above = gamma(above, code_table, base_atoms)
            if not leq_state(g_state, g_above, scheme):
                failures.append(
                    {
                        "kind": "monotonicity",
                        "state": state.as_sorted_dict(),
                        "above": above.as_sorted_dict(),
                        "gamma_state": g_state.as_sorted_dict(),
                        "gamma_above": g_above.as_sorted_dict(),
                    }
                )
                break
        if failures:
            break
    return {
        "scheme": scheme,
        "states_checked": states_checked,
        "cover_edges_checked": cover_edges_checked,
        "passed": not failures,
        "failures": failures,
    }


def verify_minimality_by_enumeration(code_table: Mapping[str, Formula], scheme: Scheme, base_atoms: Mapping[str, Value]) -> dict[str, Any]:
    codes = codes_of(code_table)
    lfp, trace = iterate_to_fixed_point(code_table, scheme, base_atoms)
    fixed_points = enumerate_fixed_points(code_table, scheme, base_atoms)
    failures = [fp.as_sorted_dict() for fp in fixed_points if not leq_state(lfp, fp, scheme)]
    return {
        "scheme": scheme,
        "codes": list(codes),
        "state_space_size": 3 ** len(codes),
        "iteration_steps_to_fixed": len(trace) - 1,
        "fixed_point_count": len(fixed_points),
        "least_fixed_point": lfp.as_sorted_dict(),
        "least_fixed_point_values": values_for_code_table(code_table, lfp, base_atoms),
        "minimality_passed": not failures,
        "nonminimal_witnesses": failures,
    }


def values_for_code_table(code_table: Mapping[str, Formula], state: State, base_atoms: Mapping[str, Value]) -> dict[str, str]:
    return {
        code: value_name(eval_formula(formula, state, code_table, base_atoms))
        for code, formula in sorted(code_table.items())
    }


# ---------------------------------------------------------------------------
# Formula generation for the first-order inertness KAT.
# ---------------------------------------------------------------------------


def formula_contains_code(formula: Formula, needle: str) -> bool:
    typ = formula["type"]
    if typ == "T":
        return formula["arg"] == needle
    if typ == "not":
        return formula_contains_code(formula["arg"], needle)
    if typ in {"and", "or"}:
        return any(formula_contains_code(arg, needle) for arg in formula["args"])
    return False


def generate_liar_free_formulas(depth: int = 2) -> list[Formula]:
    """Generate a small, exhaustive finite test language without T('liar').

    Depth 0 contains p, q, T(p), T(q), and T(truthteller).  Higher depths close
    under unary negation and binary conjunction/disjunction, with de-duplication
    by canonical JSON.
    """
    base = [Atom("p"), Atom("q"), T("p"), T("q"), T("truthteller")]
    by_depth: list[list[Formula]] = []
    seen: set[str] = set()

    def add(formula: Formula, bucket: list[Formula]) -> None:
        if formula_contains_code(formula, "liar"):
            return
        key = canonical_formula(formula)
        if key not in seen:
            seen.add(key)
            bucket.append(formula)

    d0: list[Formula] = []
    for f in base:
        add(f, d0)
    by_depth.append(d0)

    all_so_far = list(d0)
    for _ in range(1, depth + 1):
        bucket: list[Formula] = []
        for f in all_so_far:
            add(Not(f), bucket)
        for left in all_so_far:
            for right in all_so_far:
                add(And(left, right), bucket)
                add(Or(left, right), bucket)
        by_depth.append(bucket)
        all_so_far.extend(bucket)
    return all_so_far


def verify_inertness(scheme: Scheme, depth: int = 2, base_atoms: Mapping[str, Value] = BASE_ATOMS) -> dict[str, Any]:
    base_table = build_base_fragment()
    full_table = build_full_fragment()
    base_lfp, _ = iterate_to_fixed_point(base_table, scheme, base_atoms)
    full_lfp, _ = iterate_to_fixed_point(full_table, scheme, base_atoms)
    formulas = generate_liar_free_formulas(depth)
    mismatches: list[dict[str, Any]] = []
    for formula in formulas:
        v_base = value_name(eval_formula(formula, base_lfp, base_table, base_atoms))
        v_full = value_name(eval_formula(formula, full_lfp, full_table, base_atoms))
        if v_base != v_full:
            mismatches.append({"formula": formula, "base": v_base, "with_liar": v_full})
    return {
        "scheme": scheme,
        "depth": depth,
        "generated_liar_free_formula_count": len(formulas),
        "passed": not mismatches,
        "mismatches": mismatches[:20],
    }


# ---------------------------------------------------------------------------
# Classical two-valued contrast.
# ---------------------------------------------------------------------------


def eval_formula_classical(formula: Formula, true_codes: frozenset[str], code_table: Mapping[str, Formula], base_atoms_bool: Mapping[str, bool]) -> bool:
    typ = formula["type"]
    if typ == "atom":
        return base_atoms_bool[formula["name"]]
    if typ == "not":
        return not eval_formula_classical(formula["arg"], true_codes, code_table, base_atoms_bool)
    if typ == "and":
        return all(eval_formula_classical(arg, true_codes, code_table, base_atoms_bool) for arg in formula["args"])
    if typ == "or":
        return any(eval_formula_classical(arg, true_codes, code_table, base_atoms_bool) for arg in formula["args"])
    if typ == "T":
        code = formula["arg"]
        if code not in code_table:
            raise KeyError(f"Truth predicate refers to unknown code {code!r}")
        return code in true_codes
    raise ValueError(typ)


def gamma_classical(true_codes: frozenset[str], code_table: Mapping[str, Formula], base_atoms_bool: Mapping[str, bool]) -> frozenset[str]:
    return frozenset(
        code
        for code, formula in code_table.items()
        if eval_formula_classical(formula, true_codes, code_table, base_atoms_bool)
    )


def classical_fixed_points(code_table: Mapping[str, Formula]) -> list[frozenset[str]]:
    codes = codes_of(code_table)
    base_bool = {"p": True, "q": False}
    fixed: list[frozenset[str]] = []
    for bits in product([False, True], repeat=len(codes)):
        state = frozenset(code for code, bit in zip(codes, bits) if bit)
        if gamma_classical(state, code_table, base_bool) == state:
            fixed.append(state)
    return fixed


def classical_liar_oscillation(code_table: Mapping[str, Formula], steps: int = 6) -> dict[str, Any]:
    base_bool = {"p": True, "q": False}
    state = frozenset()
    trace: list[dict[str, Any]] = []
    for i in range(steps + 1):
        trace.append({"stage": i, "liar_true": "liar" in state, "true_codes": sorted(state)})
        state = gamma_classical(state, code_table, base_bool)
    return {
        "fixed_point_count": len(classical_fixed_points(code_table)),
        "trace_from_empty": trace,
        "liar_truth_sequence_from_empty": [row["liar_true"] for row in trace],
    }


# ---------------------------------------------------------------------------
# KATs and artifact generation.
# ---------------------------------------------------------------------------


def make_kat_results(depth: int = 2) -> list[dict[str, Any]]:
    full_table = build_full_fragment()
    lp_lfp, lp_trace = iterate_to_fixed_point(full_table, "lp", BASE_ATOMS)
    sk_lfp, sk_trace = iterate_to_fixed_point(full_table, "sk", BASE_ATOMS)
    lp_values = values_for_code_table(full_table, lp_lfp, BASE_ATOMS)
    sk_values = values_for_code_table(full_table, sk_lfp, BASE_ATOMS)
    classical = classical_liar_oscillation(full_table)
    inert_lp = verify_inertness("lp", depth)
    inert_sk = verify_inertness("sk", depth)
    min_lp = verify_minimality_by_enumeration(full_table, "lp", BASE_ATOMS)
    min_sk = verify_minimality_by_enumeration(full_table, "sk", BASE_ATOMS)

    kats = [
        {
            "id": "KAT-01-LP-liar-b",
            "input": "liar = not(T('liar')) in full fragment, LP least fixed point",
            "expected": "b",
            "observed": lp_values["liar"],
            "passed": lp_values["liar"] == "b",
        },
        {
            "id": "KAT-02-SK-liar-n",
            "input": "liar = not(T('liar')) in full fragment, SK least fixed point",
            "expected": "n",
            "observed": sk_values["liar"],
            "passed": sk_values["liar"] == "n",
        },
        {
            "id": "KAT-03-LP-truth-teller-b",
            "input": "truthteller = T('truthteller') in full fragment, LP least fixed point",
            "expected": "b",
            "observed": lp_values["truthteller"],
            "passed": lp_values["truthteller"] == "b",
        },
        {
            "id": "KAT-04-SK-truth-teller-n",
            "input": "truthteller = T('truthteller') in full fragment, SK least fixed point",
            "expected": "n",
            "observed": sk_values["truthteller"],
            "passed": sk_values["truthteller"] == "n",
        },
        {
            "id": "KAT-05-LP-no-explosion",
            "input": "liar_and_not_liar is designated, but q remains false and undesignated",
            "expected": {"liar_and_not_liar": "b", "liar_and_not_liar_designated": True, "q": "f", "q_designated": False},
            "observed": {
                "liar_and_not_liar": lp_values["liar_and_not_liar"],
                "liar_and_not_liar_designated": designated_lp(NAME_TO_VALUE[lp_values["liar_and_not_liar"]]),
                "q": lp_values["q"],
                "q_designated": designated_lp(NAME_TO_VALUE[lp_values["q"]]),
            },
            "passed": lp_values["liar_and_not_liar"] == "b" and lp_values["q"] == "f",
        },
        {
            "id": "KAT-06-LP-inert-liar-free",
            "input": f"add liar-containing codes, compare all generated liar-free formulae through depth {depth}",
            "expected": "no truth-value changes",
            "observed": inert_lp,
            "passed": inert_lp["passed"],
        },
        {
            "id": "KAT-07-SK-inert-liar-free",
            "input": f"add liar-containing codes, compare all generated liar-free formulae through depth {depth}",
            "expected": "no truth-value changes",
            "observed": inert_sk,
            "passed": inert_sk["passed"],
        },
        {
            "id": "KAT-08-classical-no-fixed-point",
            "input": "classical two-valued transparent liar over same finite code table",
            "expected": {"fixed_point_count": 0, "liar_oscillates_from_empty": True},
            "observed": classical,
            "passed": classical["fixed_point_count"] == 0
            and classical["liar_truth_sequence_from_empty"][:4] == [False, True, False, True],
        },
        {
            "id": "KAT-09-LP-minimality-full-enumeration",
            "input": "LP full 3^n state enumeration",
            "expected": "iterated fixed point is <= every fixed point in LP precision order",
            "observed": min_lp,
            "passed": min_lp["minimality_passed"],
        },
        {
            "id": "KAT-10-SK-minimality-full-enumeration",
            "input": "SK full 3^n state enumeration",
            "expected": "iterated fixed point is <= every fixed point in SK knowledge order",
            "observed": min_sk,
            "passed": min_sk["minimality_passed"],
        },
    ]
    return kats


def artifact_payload(depth: int = 2) -> dict[str, Any]:
    full_table = build_full_fragment()
    base_table = build_base_fragment()
    lp_lfp, lp_trace = iterate_to_fixed_point(full_table, "lp", BASE_ATOMS)
    sk_lfp, sk_trace = iterate_to_fixed_point(full_table, "sk", BASE_ATOMS)
    return {
        "schema_version": "wp6-e-c1-v1",
        "formula_schema_extension": {"added_node": {"type": "T", "arg": "<explicit finite sentence code>"}},
        "base_atoms": {k: value_name(v) for k, v in BASE_ATOMS.items()},
        "base_fragment_code_table": base_table,
        "full_fragment_code_table": full_table,
        "schemes": {
            "lp": {
                "admissible_values": ["t", "f", "b"],
                "designated_values": ["t", "b"],
                "order": "reverse inclusion on (E_plus,E_minus); b is bottom",
                "least_fixed_point": lp_lfp.as_sorted_dict(),
                "least_fixed_point_values": values_for_code_table(full_table, lp_lfp, BASE_ATOMS),
                "trace": [s.as_sorted_dict() for s in lp_trace],
            },
            "sk": {
                "admissible_values": ["t", "f", "n"],
                "designated_values": ["t"],
                "order": "inclusion on (E_plus,E_minus); n is bottom",
                "least_fixed_point": sk_lfp.as_sorted_dict(),
                "least_fixed_point_values": values_for_code_table(full_table, sk_lfp, BASE_ATOMS),
                "trace": [s.as_sorted_dict() for s in sk_trace],
            },
        },
        "inertness": {
            "lp": verify_inertness("lp", depth),
            "sk": verify_inertness("sk", depth),
        },
        "classical_contrast": classical_liar_oscillation(full_table),
    }


def enumeration_certificate_payload() -> dict[str, Any]:
    full_table = build_full_fragment()
    out = {
        "schema_version": "wp6-e-c1-enumeration-v1",
        "full_fragment_code_count": len(full_table),
        "full_fragment_codes": list(codes_of(full_table)),
        "state_space_size_per_scheme": 3 ** len(full_table),
        "monotonicity_by_cover_edges": {
            "lp": verify_monotone_by_covers(full_table, "lp", BASE_ATOMS),
            "sk": verify_monotone_by_covers(full_table, "sk", BASE_ATOMS),
        },
        "minimality_by_fixed_point_enumeration": {
            "lp": verify_minimality_by_enumeration(full_table, "lp", BASE_ATOMS),
            "sk": verify_minimality_by_enumeration(full_table, "sk", BASE_ATOMS),
        },
    }
    return out


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_all_checks(depth: int = 2) -> dict[str, Any]:
    full_table = build_full_fragment()
    kats = make_kat_results(depth)
    enum = enumeration_certificate_payload()
    checks = {
        "kat_count": len(kats),
        "kat_passed": sum(1 for item in kats if item["passed"]),
        "kat_failed_ids": [item["id"] for item in kats if not item["passed"]],
        "lp_monotone": enum["monotonicity_by_cover_edges"]["lp"]["passed"],
        "sk_monotone": enum["monotonicity_by_cover_edges"]["sk"]["passed"],
        "lp_minimal": enum["minimality_by_fixed_point_enumeration"]["lp"]["minimality_passed"],
        "sk_minimal": enum["minimality_by_fixed_point_enumeration"]["sk"]["minimality_passed"],
        "classical_fixed_points": len(classical_fixed_points(full_table)),
    }
    checks["passed"] = (
        checks["kat_failed_ids"] == []
        and checks["lp_monotone"]
        and checks["sk_monotone"]
        and checks["lp_minimal"]
        and checks["sk_minimal"]
        and checks["classical_fixed_points"] == 0
    )
    return checks


def main() -> None:
    artifact_dir = Path("experiments/wp6/artifacts")
    depth = 2
    payload = artifact_payload(depth)
    kats = make_kat_results(depth)
    enum = enumeration_certificate_payload()
    write_json(artifact_dir / "e_c1_fixed_points.json", payload)
    write_json(artifact_dir / "e_c1_kat_results.json", kats)
    write_json(artifact_dir / "e_c1_enumeration_certificates.json", enum)
    checks = run_all_checks(depth)
    if not checks["passed"]:
        raise SystemExit(f"E-C1 checks failed: {checks}")
    print(f"{checks['kat_passed']} KAT passed, 3 artifacts")


if __name__ == "__main__":
    main()
