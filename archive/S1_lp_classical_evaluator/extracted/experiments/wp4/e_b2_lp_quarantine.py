# experiments/wp4/e_b2_lp_quarantine.py
from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Sequence
from itertools import combinations
from pathlib import Path

from gl.formula import And, Formula, Iff, Imp, Not, Or, atom, bot
from lp.entailment import all_lp_valuations, entails_lp
from lp.evaluator import DESIGNATED, Lit, evaluate_lp

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
SUMMARY_PATH = ARTIFACT_DIR / "e_b2_lp_quarantine.json"
DETAILS_PATH = ARTIFACT_DIR / "e_b2_lp_quarantine_details.json"

BASE_ATOMS = ["p", "q", "r", "s"]
LAMBDA_ATOM = "lambda"
MAX_PREMISES = 2


def _unique_formulas(formulas: Iterable[Formula]) -> list[Formula]:
    seen: set[Formula] = set()
    result: list[Formula] = []
    for formula in formulas:
        if formula not in seen:
            seen.add(formula)
            result.append(formula)
    return result


def lambda_free_formula_suite(atom_names: Sequence[str]) -> list[Formula]:
    """Finite λ-free suite used by the E-B2 bounded enumeration artifact.

    The suite contains ⊥, each atom, negations of those depth-0 formulas, and
    all binary ∧/∨/→/↔ combinations of the depth-0 formulas.  It is intentionally
    finite: the experiment is an executable bounded artifact, not a proof over
    the infinite formula algebra.
    """
    depth_zero = [bot(), *(atom(name) for name in atom_names)]
    literals = [*depth_zero, *(Not(formula) for formula in depth_zero)]
    binary: list[Formula] = []
    for left in depth_zero:
        for right in depth_zero:
            binary.extend((And(left, right), Or(left, right), Imp(left, right), Iff(left, right)))
    return _unique_formulas([*literals, *binary])


def premise_sets(formulas: Sequence[Formula], max_size: int) -> Iterator[tuple[Formula, ...]]:
    yield ()
    if max_size >= 1:
        for formula in formulas:
            yield (formula,)
    if max_size >= 2:
        yield from combinations(formulas, 2)


def designated_mask(formula: Formula, valuations: Sequence[dict[str, Lit]]) -> int:
    mask = 0
    for index, valuation in enumerate(valuations):
        if evaluate_lp(formula, valuation) in DESIGNATED:
            mask |= 1 << index
    return mask


def entails_by_mask(premise_mask: int, conclusion_mask: int) -> bool:
    return (premise_mask & ~conclusion_mask) == 0


def find_mp_failure() -> dict[str, Lit]:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(a, witness) in DESIGNATED
    assert evaluate_lp(Imp(a, b), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([a, Imp(a, b)], b, ["A", "B"])
    return witness


def find_ds_failure() -> dict[str, Lit]:
    a = atom("A")
    b = atom("B")
    witness: dict[str, Lit] = {"A": "b", "B": "f"}
    assert evaluate_lp(Or(a, b), witness) in DESIGNATED
    assert evaluate_lp(Not(a), witness) in DESIGNATED
    assert evaluate_lp(b, witness) not in DESIGNATED
    assert not entails_lp([Or(a, b), Not(a)], b, ["A", "B"])
    return witness


def run_inertness_check() -> dict[str, object]:
    formulas = lambda_free_formula_suite(BASE_ATOMS)
    base_valuations = list(all_lp_valuations(BASE_ATOMS))
    full_atoms = [*BASE_ATOMS, LAMBDA_ATOM]
    full_valuations = list(all_lp_valuations(full_atoms))

    base_all_mask = (1 << len(base_valuations)) - 1
    full_all_mask = (1 << len(full_valuations)) - 1

    base_masks = {formula: designated_mask(formula, base_valuations) for formula in formulas}
    full_masks = {formula: designated_mask(formula, full_valuations) for formula in formulas}

    lam = atom(LAMBDA_ATOM)
    contradiction = And(lam, Not(lam))
    contradiction_mask = designated_mask(contradiction, full_valuations)

    violations: list[dict[str, object]] = []
    premise_set_count = 0
    comparison_count = 0

    for premises in premise_sets(formulas, MAX_PREMISES):
        premise_set_count += 1
        base_premise_mask = base_all_mask
        full_premise_mask = full_all_mask
        for premise in premises:
            base_premise_mask &= base_masks[premise]
            full_premise_mask &= full_masks[premise]

        quarantined_premise_mask = full_premise_mask & contradiction_mask

        for conclusion in formulas:
            comparison_count += 1
            right = entails_by_mask(base_premise_mask, base_masks[conclusion])
            left = entails_by_mask(quarantined_premise_mask, full_masks[conclusion])
            if left != right:
                violations.append(
                    {
                        "premises": [premise.to_json() for premise in premises],
                        "conclusion": conclusion.to_json(),
                        "with_lambda_contradiction": left,
                        "without_lambda_contradiction": right,
                    }
                )
                if len(violations) >= 10:
                    break
        if len(violations) >= 10:
            break

    return {
        "inert": not violations,
        "violations": violations,
        "base_atoms": BASE_ATOMS,
        "formula_count": len(formulas),
        "premise_set_count": premise_set_count,
        "max_premises": MAX_PREMISES,
        "base_valuation_count": len(base_valuations),
        "full_valuation_count": len(full_valuations),
        "comparison_count": comparison_count,
        "lambda_contradiction_designated_full_valuations": contradiction_mask.bit_count(),
    }


def run() -> dict[str, object]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    lam = atom(LAMBDA_ATOM)
    liar = Iff(lam, Not(lam))
    witness: dict[str, Lit] = {LAMBDA_ATOM: "b"}
    liar_value = evaluate_lp(liar, witness)
    satisfiable = liar_value in DESIGNATED

    inertness = run_inertness_check()
    mp_failure = find_mp_failure()
    ds_failure = find_ds_failure()

    summary = {
        "satisfiable": satisfiable,
        "inert": inertness["inert"],
        "mp_failure": mp_failure,
        "ds_failure": ds_failure,
    }
    details = {
        **summary,
        "liar_formula": liar.to_json(),
        "liar_witness": witness,
        "liar_value_at_witness": liar_value,
        "inertness": inertness,
    }

    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    DETAILS_PATH.write_text(json.dumps(details, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
