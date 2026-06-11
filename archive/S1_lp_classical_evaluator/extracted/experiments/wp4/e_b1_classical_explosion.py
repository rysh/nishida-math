# experiments/wp4/e_b1_classical_explosion.py
from __future__ import annotations

import json
from pathlib import Path

from classical.entailment import all_classical_valuations, entails_classical
from classical.evaluator import evaluate_classical
from gl.formula import And, Iff, Not, atom, bot

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
SUMMARY_PATH = ARTIFACT_DIR / "e_b1_classical_explosion.json"
DETAILS_PATH = ARTIFACT_DIR / "e_b1_classical_explosion_details.json"


def run() -> dict[str, object]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    lam = atom("lambda")
    liar = Iff(lam, Not(lam))
    lambda_atoms = ["lambda"]

    enumeration = [
        {
            "valuation": valuation,
            "value": evaluate_classical(liar, valuation),
        }
        for valuation in all_classical_valuations(lambda_atoms)
    ]
    satisfiable = any(row["value"] for row in enumeration)

    # Representative conclusions.  Since no valuation satisfies λ↔¬λ, the
    # entailment check is vacuous for every conclusion over the chosen atom set.
    p = atom("p")
    sample_conclusions = [
        bot(),
        p,
        Not(p),
        And(p, Not(p)),
        Iff(lam, Not(lam)),
    ]
    vacuity_checks = [
        entails_classical([liar], conclusion, ["lambda", "p"])
        for conclusion in sample_conclusions
    ]
    vacuous_explosion = (not satisfiable) and all(vacuity_checks)

    summary = {
        "satisfiable": satisfiable,
        "vacuous_explosion": vacuous_explosion,
        "enumeration_size": len(enumeration),
    }
    details = {
        **summary,
        "formula": liar.to_json(),
        "enumeration": enumeration,
        "sample_conclusions": [conclusion.to_json() for conclusion in sample_conclusions],
        "sample_vacuity_checks": vacuity_checks,
    }

    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    DETAILS_PATH.write_text(json.dumps(details, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
