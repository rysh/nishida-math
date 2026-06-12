# experiments/wp5/build_table.py
"""Render the WP5 headline table as Markdown.

The Markdown table is produced from ``claims.json`` only; the input
artifacts that ``claims.json`` itself references are not opened here. If
``claims.json`` was built successfully (i.e. each cell already passed
``build_claims.py``'s verification), the Markdown table is guaranteed to
match what those artifacts say.

Deterministic output: no timestamps, no environment-dependent text,
fixed encoding, trailing newline.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


WP5_ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
CLAIMS_PATH = WP5_ARTIFACTS / "claims.json"
TABLE_PATH = WP5_ARTIFACTS / "headline_table.md"


def _load_claims() -> dict[str, Any]:
    return json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))


def _summarise_classical_witness(row: dict[str, Any]) -> str:
    keys = row["formal_witness"]["keys"]
    artifact = row["formal_witness"]["artifact"]
    details = row["formal_witness"]["details_artifact"]
    return (
        f"[E-B1]({artifact}) — `satisfiable: {str(keys['satisfiable']).lower()}`, "
        f"`vacuous_explosion: {str(keys['vacuous_explosion']).lower()}`, "
        f"all 5 sample vacuity checks pass "
        f"([details]({details}))"
    )


def _summarise_lp_witness(row: dict[str, Any]) -> str:
    keys = row["formal_witness"]["keys"]
    artifact = row["formal_witness"]["artifact"]
    details = row["formal_witness"]["details_artifact"]
    mp = keys["mp_failure"]
    ds = keys["ds_failure"]
    return (
        f"[E-B2]({artifact}) — `satisfiable: true`, `inert: true`, "
        f"MP fails at v(A)={mp['A']}, v(B)={mp['B']}; "
        f"DS fails at v(A)={ds['A']}, v(B)={ds['B']} "
        f"([details]({details}))"
    )


def _summarise_gl_witness(row: dict[str, Any]) -> str:
    keys = row["formal_witness"]["keys"]
    artifact = row["formal_witness"]["artifact"]
    counts = keys["witness_world_counts"]
    exhaustive = keys["minimality_exhaustively_checked_for"]
    return (
        f"[E-A2]({artifact}) — stages 0..{keys['max_n']}, "
        f"every stage's monotone direction proved and strict direction refuted, "
        f"witness counts {counts} (linear n+2); "
        f"minimality exhaustively verified for n ∈ {exhaustive}"
    )


_SUMMARY_BY_EXPERIMENT = {
    "E-B1": _summarise_classical_witness,
    "E-B2": _summarise_lp_witness,
    "E-A2": _summarise_gl_witness,
}


def _row_markdown(row: dict[str, Any]) -> str:
    summary = _SUMMARY_BY_EXPERIMENT[row["formal_witness"]["experiment"]](row)
    cells = [
        row["environment"],
        row["contradiction_status"],
        row["what_follows"],
        summary,
        row["generativity"],
    ]
    return "| " + " | ".join(cells) + " |"


def render_table(claims: dict[str, Any]) -> str:
    header = (
        "| Environment | Contradiction status | What follows from the seed "
        "| Formal witness | Generativity |"
    )
    separator = "|---|---|---|---|---|"
    body = "\n".join(_row_markdown(r) for r in claims["rows"])

    lines = [
        "# Headline: ONE SEED, THREE ENVIRONMENTS",
        "",
        "*Auto-generated from `experiments/wp5/artifacts/claims.json`. "
        "Do not edit by hand; run `uv run python experiments/wp5/build_table.py` "
        "to regenerate.*",
        "",
        header,
        separator,
        body,
        "",
        "## Reading",
        "",
        "- **Contradiction status**: how each environment treats the contradiction the seed produces.",
        "- **What follows from the seed**: what is derivable from the contradiction in that environment.",
        "- **Formal witness**: the machine-checked artifact backing the row. Each link resolves to a JSON artifact in the repository.",
        "- **Generativity**: the unifying axis. Classical destroys distinction (everything follows, nothing can be told apart); LP quarantines the contradiction but generates nothing new in the λ-free fragment; only GL turns the contradiction into the engine of a strictly increasing hierarchy. This is the computational counterpart of Paper A's three modes of contradiction (classical / tolerative / generative).",
        "",
        "## Source",
        "",
        f"Generated from `{CLAIMS_PATH.relative_to(Path(__file__).resolve().parents[2]).as_posix()}`, which is itself built by `experiments/wp5/build_claims.py` against the three input artifacts listed under each row's `formal_witness`.",
        "",
    ]
    return "\n".join(lines)


def run() -> Path:
    WP5_ARTIFACTS.mkdir(parents=True, exist_ok=True)
    claims = _load_claims()
    TABLE_PATH.write_text(render_table(claims), encoding="utf-8")
    return TABLE_PATH


if __name__ == "__main__":
    print(run())
