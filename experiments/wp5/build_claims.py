# experiments/wp5/build_claims.py
"""Build the WP5 headline claims manifest.

The simulation spec §1 lays out a 3-row Headline experiment (one seed,
three environments). This script collects the formal witnesses from the
three machine-checked experiments (E-B1 classical explosion, E-B2 LP
quarantine, E-A2 GL ladder) into a single ``claims.json`` that the table
and figure renderers consume. ``claims.json`` is the single source of
truth so the Markdown table and the SVG figure can never drift apart.

The script also verifies each cell against its input artifact before
writing the manifest: if any expected value disagrees with what the
artifact actually says, the manifest is not written and an
``AssertionError`` propagates. This pins the spec's central claim — that
the contradiction is destroyed in classical logic, quarantined in LP,
and resolved by ascent in GL — to running code, not to prose.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
WP3_ARTIFACTS = REPO_ROOT / "experiments" / "wp3" / "artifacts"
WP4_ARTIFACTS = REPO_ROOT / "experiments" / "wp4" / "artifacts"
WP5_ARTIFACTS = Path(__file__).resolve().parent / "artifacts"

CLASSICAL_SUMMARY = WP4_ARTIFACTS / "e_b1_classical_explosion.json"
CLASSICAL_DETAILS = WP4_ARTIFACTS / "e_b1_classical_explosion_details.json"
LP_SUMMARY = WP4_ARTIFACTS / "e_b2_lp_quarantine.json"
LP_DETAILS = WP4_ARTIFACTS / "e_b2_lp_quarantine_details.json"
GL_MANIFEST = WP3_ARTIFACTS / "ladder_manifest.json"

CLAIMS_PATH = WP5_ARTIFACTS / "claims.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _check(label: str, condition: bool, detail: str) -> None:
    if not condition:
        raise AssertionError(f"{label}: claim not backed by artifact: {detail}")


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _classical_row() -> dict[str, Any]:
    summary = _load(CLASSICAL_SUMMARY)
    details = _load(CLASSICAL_DETAILS)
    _check("classical", summary["satisfiable"] is False, "liar must be unsatisfiable")
    _check("classical", summary["vacuous_explosion"] is True, "vacuous_explosion must be true")
    sample_checks = details["sample_vacuity_checks"]
    _check(
        "classical",
        isinstance(sample_checks, list) and len(sample_checks) >= 5 and all(sample_checks),
        f"all sample vacuity checks must pass; got {sample_checks!r}",
    )
    return {
        "environment": "Classical propositional logic",
        "seed": "liar constraint λ ↔ ¬λ",
        "contradiction_status": "explodes",
        "what_follows": "everything (vacuous entailment)",
        "formal_witness": {
            "experiment": "E-B1",
            "artifact": _relative(CLASSICAL_SUMMARY),
            "keys": {
                "satisfiable": summary["satisfiable"],
                "vacuous_explosion": summary["vacuous_explosion"],
                "enumeration_size": summary["enumeration_size"],
            },
            "details_artifact": _relative(CLASSICAL_DETAILS),
            "details_keys": {
                "sample_vacuity_checks": sample_checks,
            },
        },
        "generativity": "destroyed (everything derivable, nothing distinguishable)",
    }


def _lp_row() -> dict[str, Any]:
    summary = _load(LP_SUMMARY)
    details = _load(LP_DETAILS)
    _check("lp", summary["satisfiable"] is True, "liar must be satisfiable in LP")
    _check("lp", summary["inert"] is True, "inertness check must pass")
    expected_witness = {"A": "b", "B": "f"}
    _check(
        "lp",
        summary["mp_failure"] == expected_witness,
        f"MP failure witness must be {expected_witness!r}; got {summary['mp_failure']!r}",
    )
    _check(
        "lp",
        summary["ds_failure"] == expected_witness,
        f"DS failure witness must be {expected_witness!r}; got {summary['ds_failure']!r}",
    )
    _check(
        "lp",
        details["liar_witness"] == {"lambda": "b"},
        f"liar witness must be lambda=b; got {details['liar_witness']!r}",
    )
    _check(
        "lp",
        details["liar_value_at_witness"] == "b",
        f"liar value at witness must be 'b'; got {details['liar_value_at_witness']!r}",
    )
    inertness = details["inertness"]
    _check(
        "lp",
        inertness["inert"] is True and inertness["violations"] == [],
        "inertness check details must show zero violations",
    )
    return {
        "environment": "LP (Priest's Logic of Paradox)",
        "seed": "same liar constraint λ ↔ ¬λ",
        "contradiction_status": "tolerated",
        "what_follows": "nothing new in the λ-free language (inert)",
        "formal_witness": {
            "experiment": "E-B2",
            "artifact": _relative(LP_SUMMARY),
            "keys": {
                "satisfiable": summary["satisfiable"],
                "inert": summary["inert"],
                "mp_failure": summary["mp_failure"],
                "ds_failure": summary["ds_failure"],
            },
            "details_artifact": _relative(LP_DETAILS),
            "details_keys": {
                "liar_witness": details["liar_witness"],
                "liar_value_at_witness": details["liar_value_at_witness"],
                "inertness_scope": {
                    "base_atoms": inertness["base_atoms"],
                    "formula_count": inertness["formula_count"],
                    "max_premises": inertness["max_premises"],
                    "premise_set_count": inertness["premise_set_count"],
                    "comparison_count": inertness["comparison_count"],
                    "violations": inertness["violations"],
                },
            },
        },
        "generativity": "zero (contradiction quarantined, no new λ-free consequences)",
    }


def _gl_row() -> dict[str, Any]:
    manifest = _load(GL_MANIFEST)
    stages = manifest["stages"]
    _check("gl", manifest["max_n"] == 8, f"max_n must be 8; got {manifest['max_n']!r}")
    _check(
        "gl",
        manifest["exhaustive_max"] == 4,
        f"exhaustive_max must be 4; got {manifest['exhaustive_max']!r}",
    )
    _check("gl", len(stages) == 9, f"stages must have 9 entries; got {len(stages)}")

    monotone_statuses = [s["monotone_status"] for s in stages]
    strict_statuses = [s["strict_status"] for s in stages]
    countermodel_verified = [s["countermodel_verified"] for s in stages]
    witness_counts = [s["witness_world_count"] for s in stages]
    expected_counts = list(range(2, 11))
    _check(
        "gl",
        all(s == "proved" for s in monotone_statuses),
        "every stage's monotone direction must be proved",
    )
    _check(
        "gl",
        all(s == "refuted" for s in strict_statuses),
        "every stage's strict direction must be refuted",
    )
    _check(
        "gl",
        all(countermodel_verified),
        "every stage's stored countermodel must be independently verified",
    )
    _check(
        "gl",
        witness_counts == expected_counts,
        f"witness counts must match n+2 across n=0..8; expected {expected_counts}, got {witness_counts}",
    )
    exhaustive = [s["minimality_exhaustively_checked"] for s in stages]
    _check(
        "gl",
        exhaustive[:5] == [True] * 5 and exhaustive[5:] == [False] * 4,
        f"exhaustive minimality must be checked exactly for n=0..4; got {exhaustive}",
    )

    return {
        "environment": "GL (Gödel-Löb provability logic)",
        "seed": "Gödelian fixed point H ↔ ¬□H",
        "contradiction_status": "resolved by ascent",
        "what_follows": "a strictly higher consistency level (Con_n ⊊ Con_{n+1})",
        "formal_witness": {
            "experiment": "E-A2",
            "artifact": _relative(GL_MANIFEST),
            "keys": {
                "max_n": manifest["max_n"],
                "exhaustive_max": manifest["exhaustive_max"],
                "all_monotone_proved": True,
                "all_strict_refuted": True,
                "all_countermodels_verified": True,
                "witness_world_counts": witness_counts,
                "minimality_exhaustively_checked_for": [s["stage"] for s in stages if s["minimality_exhaustively_checked"]],
            },
        },
        "generativity": "unbounded (each stage requires a strictly deeper frame; linear n+2)",
    }


def build_claims_data() -> dict[str, Any]:
    return {
        "spec": (
            "Headline §1 of the simulation spec: one self-referential seed, "
            "three logical environments. Every cell is backed by a "
            "machine-checked artifact, and the values shown here were "
            "validated against the source artifacts at build time."
        ),
        "columns": [
            "contradiction_status",
            "what_follows",
            "formal_witness",
            "generativity",
        ],
        "rows": [_classical_row(), _lp_row(), _gl_row()],
    }


def run() -> dict[str, Any]:
    WP5_ARTIFACTS.mkdir(parents=True, exist_ok=True)
    data = build_claims_data()
    CLAIMS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


if __name__ == "__main__":
    data = run()
    print(json.dumps({"rows": [r["environment"] for r in data["rows"]]}, ensure_ascii=False, indent=2))
