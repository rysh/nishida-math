# experiments/wp3/build_ladder.py
"""Build the WP3 ladder data manifest.

For each stage ``n = 0..max_n`` (default 8), collect:

* the ``(Monotone)`` certificate that ``GL ⊢ Con_{n+1} → Con_n``
  (i.e. ``prove_gl(...).status == 'proved'``);
* the ``(Strict)`` refutation that ``GL ⊬ Con_n → Con_{n+1}``
  (i.e. ``prove_gl(...).status == 'refuted'``), together with an
  independently verified countermodel JSON (loaded from
  ``experiments/wp3/countermodels/strict_n{n}.json``);
* the theoretical minimal witness world count ``n + 2``;
* for ``n <= exhaustive_max`` (default 4), an *exhaustive* check that no
  GL frame on fewer than ``n + 2`` worlds can refute
  ``Imp(Con(n), Con(n + 1))`` at world 0.

Every claim that appears in the manifest carries either a prover
certificate or an independently verified countermodel. Frame evaluation
during the minimality search goes through
``gl.countermodel_verifier.verify_countermodel`` so the engine does not
grade itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gl.countermodel_verifier import verify_countermodel
from gl.formula import Box, Formula, Imp, Not, bot, modal_depth
from gl.kripke_search import enumerate_finite_gl_frames
from gl.tableau import prove_gl


def Con(n: int) -> Formula:
    """Con_n by the recursive definition (mirror of build_countermodels.Con).

    Kept inline to avoid cross-script imports when this module is loaded
    by pytest (the experiments directory is not on ``pythonpath``).
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
COUNTERMODEL_DIR = Path(__file__).resolve().parent / "countermodels"
MANIFEST_PATH = ARTIFACT_DIR / "ladder_manifest.json"


def _frame_to_model_json(
    num_worlds: int,
    rel: tuple[tuple[int, int], ...],
    formula: Formula,
) -> dict[str, Any]:
    """Wrap a frame in the Kripke model JSON schema that verify_countermodel
    expects. The valuation is empty because every formula we feed to it
    here is letterless (built from ``Con(n)``)."""
    return {
        "worlds": list(range(num_worlds)),
        "rel": [list(edge) for edge in rel],
        "val": {},
        "refutes": {"formula": formula.to_json(), "at": 0},
        "checks": {"transitive": True, "irreflexive": True},
    }


def _exhaustive_minimality_check(n: int) -> dict[str, Any]:
    """For ``n``, check by exhaustion that no GL frame on ``m`` worlds with
    ``m < n + 2`` refutes ``Imp(Con(n), Con(n + 1))`` at world 0.

    Combined with the (n+2)-chain countermodel from
    ``experiments/wp3/countermodels/strict_n{n}.json``, this pins the
    minimal witness world count to exactly ``n + 2``.
    """
    formula = Imp(Con(n), Con(n + 1))
    target_count = n + 2
    height_bound = modal_depth(formula)
    frames_examined = 0
    for m in range(1, target_count):
        for rel in enumerate_finite_gl_frames(m, height_bound=height_bound):
            frames_examined += 1
            model = _frame_to_model_json(m, rel, formula)
            if verify_countermodel(formula, model):
                return {
                    "smaller_countermodel_found_at": m,
                    "frames_examined": frames_examined,
                    "ok": False,
                    "violating_frame": {"num_worlds": m, "rel": [list(e) for e in rel]},
                }
    return {
        "smallest_frame_size_tried": 1,
        "largest_frame_size_tried": target_count - 1,
        "frames_examined": frames_examined,
        "ok": True,
    }


def _load_countermodel(n: int) -> dict[str, Any]:
    path = COUNTERMODEL_DIR / f"strict_n{n}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_record(n: int, *, exhaustive_max: int) -> dict[str, Any]:
    monotone_formula = Imp(Con(n + 1), Con(n))
    strict_formula = Imp(Con(n), Con(n + 1))

    monotone_result = prove_gl(monotone_formula)
    strict_result = prove_gl(strict_formula)

    model = _load_countermodel(n)
    countermodel_verified = verify_countermodel(strict_formula, model)

    record: dict[str, Any] = {
        "stage": n,
        "monotone_status": monotone_result.status,
        "strict_status": strict_result.status,
        "witness_world_count": n + 2,
        "countermodel_path": f"experiments/wp3/countermodels/strict_n{n}.json",
        "countermodel_verified": countermodel_verified,
        "minimality_exhaustively_checked": n <= exhaustive_max,
    }

    if n <= exhaustive_max:
        check = _exhaustive_minimality_check(n)
        record["minimality_check"] = check
        if not check["ok"]:
            raise AssertionError(
                f"minimality assumption broken at n={n}: "
                f"a smaller frame refutes Con_{n} -> Con_{n + 1}"
            )

    if monotone_result.status != "proved":
        raise AssertionError(f"Con_{n + 1} -> Con_{n} unexpectedly not proved")
    if strict_result.status != "refuted":
        raise AssertionError(f"Con_{n} -> Con_{n + 1} unexpectedly not refuted")
    if not countermodel_verified:
        raise AssertionError(
            f"stored countermodel for n={n} does not refute the target at world 0"
        )

    return record


def build_ladder_data(max_n: int = 8, exhaustive_max: int = 4) -> dict[str, Any]:
    if max_n < 0:
        raise ValueError("max_n must be non-negative")
    if exhaustive_max < 0 or exhaustive_max > max_n:
        raise ValueError("exhaustive_max must be in [0, max_n]")

    stages = [_stage_record(n, exhaustive_max=exhaustive_max) for n in range(max_n + 1)]
    return {
        "spec": (
            "GL hierarchy of iterated consistency; minimal witness world "
            "count grows as n + 2."
        ),
        "max_n": max_n,
        "exhaustive_max": exhaustive_max,
        "stages": stages,
    }


def run() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data = build_ladder_data(max_n=8, exhaustive_max=5)
    MANIFEST_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


if __name__ == "__main__":
    summary = run()
    counts = {s["stage"]: s["witness_world_count"] for s in summary["stages"]}
    print(json.dumps({"witness_world_counts": counts}, ensure_ascii=False, indent=2))
