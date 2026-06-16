"""E-A3: Gödel seed launches, Henkin seed flatlines — same engine, same measure.

The point of E-A3 is structural: feed two self-referential seeds into *the same*
fixed-point engine, varying only the negation around `□p` in the body, and
observe that one seed reduces to `Con_0 = ¬□⊥` (which is *not* a GL theorem and
is exactly what the E-A2 hierarchy of `experiments/wp3/` is built on) while the
other reduces to `⊤` (a GL theorem, which adds nothing when adjoined as an
axiom). The active ingredient of generation is the negative self-reference
structure `¬□p`, not contradiction.

The single function shared between the two sides is
`gl.fixed_point.fixed_point`. The single Boolean decision procedure used to
classify both sides is `gl.tableau.prove_gl`. The single closed-fragment
measure used to compare both sides is GL-equivalence in the letterless
fragment via `gl.letterless.nf_equiv`. The seeds themselves differ by exactly
one connective: `¬□p` versus `□p`.

Three JSON artifacts are emitted:

* `e_a3_godel_vs_henkin.json` — the side-by-side summary
* `e_a3_godel_no_new_letterless.json` — countermodel-backed evidence that
  the Gödel seed (Con_0) does not prove higher `Con_{n+1}` consequences
* `e_a3_henkin_flatline.json` — letterless witnesses that the Henkin seed,
  when adjoined to a theory, adds no new letterless theorems
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

from gl.fixed_point import fixed_point
from gl.formula import Box, Iff, Imp, Not, atom, bot, box_power, con
from gl.letterless import nf_equiv
from gl.tableau import prove_gl


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


# ---------------------------------------------------------------------------
# The two seeds, differing by one connective.
# ---------------------------------------------------------------------------

P = "p"
GODEL_SEED_BODY = Not(Box(atom(P)))   # ¬□p
HENKIN_SEED_BODY = Box(atom(P))        # □p


def _engine_source_location() -> dict[str, Any]:
    src_file = inspect.getsourcefile(fixed_point)
    return {
        "function": "fixed_point",
        "module": fixed_point.__module__,
        "source_file": Path(src_file).name if src_file else None,
    }


def _seed_body_delta() -> dict[str, Any]:
    """Document, in JSON, that the two seed bodies differ by exactly one
    application of negation around ``□p``.
    """
    godel_json = GODEL_SEED_BODY.to_json()
    henkin_json = HENKIN_SEED_BODY.to_json()
    return {
        "godel_body_json": godel_json,
        "henkin_body_json": henkin_json,
        "structural_relation": "godel_body == {'type': 'not', 'arg': henkin_body}",
        "structural_check": godel_json == {"type": "not", "arg": henkin_json},
    }


def _build_summary() -> dict[str, Any]:
    H_godel = fixed_point(GODEL_SEED_BODY, P)
    H_henkin = fixed_point(HENKIN_SEED_BODY, P)

    con0 = con(0)                    # ¬□⊥
    top = Not(bot())                 # ⊤

    return {
        "engine": _engine_source_location(),
        "seed_delta": _seed_body_delta(),
        "godel_seed": {
            "body_pretty": "Not(Box(atom(p)))",
            "fixed_point_pretty": str(H_godel),
            "fixed_point_json": H_godel.to_json(),
            "reduces_to_in_gl": "¬□⊥ (Con_0)",
            "gl_proves_reduction_to_con0": (
                prove_gl(Iff(H_godel, con0)).status == "proved"
            ),
            "letterless_nf_equiv_con0": nf_equiv(H_godel, con0),
            "is_gl_theorem": prove_gl(H_godel).status == "proved",
            "launches_hierarchy": True,
            "hierarchy_artifact": "experiments/wp3/artifacts/ladder_manifest.json",
            "measure_growth": "n+2 (linear) — see Con_n countermodel chain",
        },
        "henkin_seed": {
            "body_pretty": "Box(atom(p))",
            "fixed_point_pretty": str(H_henkin),
            "fixed_point_json": H_henkin.to_json(),
            "reduces_to_in_gl": "⊤",
            "gl_proves_reduction_to_top": (
                prove_gl(Iff(H_henkin, top)).status == "proved"
            ),
            "letterless_nf_equiv_top": nf_equiv(H_henkin, top),
            "is_gl_theorem": prove_gl(H_henkin).status == "proved",
            "launches_hierarchy": False,
            "measure_growth": "zero — see e_a3_henkin_flatline.json",
        },
        "interpretation": (
            "The two seeds, differing by exactly one negation around □p, are "
            "fed through the same fixed-point function and classified by the "
            "same GL prover on the same letterless fragment. The Gödel seed "
            "reduces to ¬□⊥ (Con_0), which is not a GL theorem and is the "
            "first rung of the E-A2 ladder. The Henkin seed reduces to ⊤, "
            "which is a GL theorem and adds nothing when adjoined. This is "
            "an instantiation of Boolos 1993 (Löb's theorem applied to the "
            "Henkin fixed point), not new mathematics. The §4 metric framing "
            "is: Gödel-seed generativity = unbounded (linear n+2), "
            "Henkin-seed generativity = zero."
        ),
    }


def _build_godel_no_new_letterless(max_n: int = 4) -> dict[str, Any]:
    """For each n in [0, max_n], record the GL verdict on Con_0 → Con_{n+1}.

    All n ≥ 0 should be refuted: the strict-n+1 chain countermodels of E-A2
    refute these too because the only premise (Con_0) holds vacuously in those
    frames. This shows that the Gödel seed (Con_0), even when adjoined as a
    premise, does not generate higher Con_{n+1} as a consequence — the higher
    rungs must each be adjoined separately, which is exactly the E-A2 ladder.
    """
    H_godel = fixed_point(GODEL_SEED_BODY, P)
    stages = []
    for n in range(max_n + 1):
        target = con(n + 1)
        status = prove_gl(Imp(H_godel, target)).status
        stages.append({
            "premise": "H_godel (= Con_0)",
            "target": f"Con_{n + 1}",
            "gl_status": status,
            "interpretation": (
                "Con_0 does not entail this higher consequence; "
                "the higher rung is genuinely new."
                if status == "refuted"
                else "unexpected proved status — investigate"
            ),
        })
    return {
        "engine": _engine_source_location(),
        "premise_formula_pretty": str(H_godel),
        "ladder_reference": "experiments/wp3/artifacts/ladder_manifest.json",
        "stages": stages,
    }


def _henkin_letterless_sample() -> list[Any]:
    """Small letterless sample to demonstrate the Henkin flatline measure."""
    return [
        bot(),                                # ⊥
        Not(bot()),                           # ⊤
        Box(bot()),                           # □⊥
        Not(Box(bot())),                      # Con_0
        con(1),                               # Con_1
        con(2),                               # Con_2
        box_power(bot(), 3),                  # □³⊥
    ]


def _build_henkin_flatline() -> dict[str, Any]:
    """For each letterless B in the sample, verify GL ⊢ (K → B) ↔ B.

    K is the Henkin fixed point. GL proves K ↔ ⊤, hence GL ⊢ (K → B) ↔ B for
    every B. This is the precise sense in which adjoining K as an axiom adds
    no new letterless theorems: the consequence set is unchanged.
    """
    H_henkin = fixed_point(HENKIN_SEED_BODY, P)
    witnesses = []
    for B in _henkin_letterless_sample():
        equivalence = Iff(Imp(H_henkin, B), B)
        result = prove_gl(equivalence)
        witnesses.append({
            "B_pretty": str(B),
            "B_json": B.to_json(),
            "gl_proves_K_implies_B_iff_B": result.status == "proved",
        })
    all_unchanged = all(w["gl_proves_K_implies_B_iff_B"] for w in witnesses)
    return {
        "engine": _engine_source_location(),
        "henkin_fp_pretty": str(H_henkin),
        "claim": (
            "For every B in the letterless sample, GL ⊢ (K → B) ↔ B; "
            "hence adjoining K as an axiom adds no new letterless theorems."
        ),
        "all_unchanged": all_unchanged,
        "witnesses": witnesses,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    summary = _build_summary()
    godel_chain = _build_godel_no_new_letterless()
    henkin_flatline = _build_henkin_flatline()

    _write_json(ARTIFACT_DIR / "e_a3_godel_vs_henkin.json", summary)
    _write_json(ARTIFACT_DIR / "e_a3_godel_no_new_letterless.json", godel_chain)
    _write_json(ARTIFACT_DIR / "e_a3_henkin_flatline.json", henkin_flatline)

    godel = summary["godel_seed"]
    henkin = summary["henkin_seed"]
    delta_ok = summary["seed_delta"]["structural_check"]
    flatline_ok = henkin_flatline["all_unchanged"]
    chain_ok = all(s["gl_status"] == "refuted" for s in godel_chain["stages"])

    print(
        "E-A3: "
        f"seeds differ by one Not = {delta_ok}; "
        f"godel→Con_0 = {godel['gl_proves_reduction_to_con0']} "
        f"(godel is GL theorem? {godel['is_gl_theorem']}); "
        f"henkin→⊤ = {henkin['gl_proves_reduction_to_top']} "
        f"(henkin is GL theorem? {henkin['is_gl_theorem']}); "
        f"godel chain all refuted = {chain_ok}; "
        f"henkin flatline = {flatline_ok}."
    )

    if not (delta_ok and chain_ok and flatline_ok):
        raise SystemExit("E-A3 checks failed; see artifacts for details.")


if __name__ == "__main__":
    main()
