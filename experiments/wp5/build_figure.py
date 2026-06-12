# experiments/wp5/build_figure.py
"""Render the WP5 headline figure as a deterministic SVG.

The figure is the same 3-row table as ``headline_table.md`` but rendered
visually, with extra emphasis on the *Generativity* column — the axis
that distinguishes generative contradiction (GL) from the destructive
(Classical) and tolerative (LP) handling of the same self-referential
seed. The ``Formal witness`` column is intentionally omitted from the
SVG because the JSON-path references are far more useful as Markdown
links than as in-figure text.

The renderer follows the same determinism contract as
``experiments/wp3/build_figure.py``: fixed backend, fixed ``svg.hashsalt``,
fonts embedded as paths, no timestamp metadata. Two consecutive runs
produce byte-identical files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


WP5_ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
CLAIMS_PATH = WP5_ARTIFACTS / "claims.json"
FIGURE_PATH = WP5_ARTIFACTS / "headline_figure.svg"


_GENERATIVITY_PALETTE = {
    "Classical propositional logic": "#fbe2dc",  # warm red — destruction
    "LP (Priest's Logic of Paradox)": "#fdf3c4",  # muted yellow — inertness
    "GL (Gödel-Löb provability logic)": "#dde8f7",  # cool blue — ascent
}

_GENERATIVITY_GLYPH = {
    "Classical propositional logic": "⊥ ⊢ everything",
    "LP (Priest's Logic of Paradox)": "0 (flatline)",
    "GL (Gödel-Löb provability logic)": "2 → 3 → 4 → … → n+2",
}


def _load_claims() -> dict[str, Any]:
    return json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))


def _setup_determinism() -> None:
    plt.rcParams["svg.hashsalt"] = "wp5-headline"
    plt.rcParams["svg.fonttype"] = "path"
    plt.rcParams["pdf.fonttype"] = 42


def render_headline(claims: dict[str, Any], output_path: Path) -> Path:
    _setup_determinism()

    rows = claims["rows"]
    headers = [
        "Environment",
        "Contradiction status",
        "What follows from the seed",
        "Generativity",
    ]
    col_widths = [0.28, 0.18, 0.30, 0.24]

    fig, ax = plt.subplots(figsize=(11.0, 4.4), dpi=100)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    header_height = 0.16
    row_height = (1.0 - header_height) / len(rows)

    # Header band.
    ax.add_patch(
        Rectangle(
            (0, 1 - header_height),
            1,
            header_height,
            facecolor="#26405e",
            edgecolor="#26405e",
            zorder=1,
        )
    )
    x = 0.0
    for header, width in zip(headers, col_widths):
        ax.text(
            x + width / 2,
            1 - header_height / 2,
            header,
            ha="center",
            va="center",
            color="white",
            fontsize=10,
            fontweight="bold",
            zorder=2,
        )
        x += width

    # Body rows.
    for i, row in enumerate(rows):
        y_top = 1 - header_height - i * row_height
        y_bottom = y_top - row_height
        env = row["environment"]
        background = _GENERATIVITY_PALETTE.get(env, "white")

        # Stripe across the whole row so the colour reading is consistent
        # with the generativity glyph in the last column.
        ax.add_patch(
            Rectangle(
                (0, y_bottom),
                1,
                row_height,
                facecolor=background,
                edgecolor="#999999",
                linewidth=0.5,
                zorder=1,
            )
        )

        cells = [
            row["environment"],
            row["contradiction_status"],
            row["what_follows"],
            row["generativity"],
        ]
        x = 0.0
        for col_index, (cell, width) in enumerate(zip(cells, col_widths)):
            text = cell
            fontweight = "normal"
            color = "#1a1a1a"
            if col_index == 3:  # Generativity column gets the glyph + bold.
                glyph = _GENERATIVITY_GLYPH.get(env)
                if glyph:
                    text = f"{cell}\n{glyph}"
                fontweight = "bold"
                color = "#26405e"
            ax.text(
                x + width / 2,
                (y_top + y_bottom) / 2,
                text,
                ha="center",
                va="center",
                color=color,
                fontsize=8.5,
                fontweight=fontweight,
                wrap=True,
                zorder=2,
            )
            x += width

    fig.suptitle(
        "ONE SEED, THREE ENVIRONMENTS",
        fontsize=12,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.02,
        "Auto-generated from experiments/wp5/artifacts/claims.json — every cell carries a machine-checked witness.",
        ha="center",
        fontsize=7,
        color="#555555",
    )

    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(
        output_path,
        format="svg",
        metadata={"Date": None, "Creator": None},
    )
    plt.close(fig)
    return output_path


def run() -> Path:
    WP5_ARTIFACTS.mkdir(parents=True, exist_ok=True)
    claims = _load_claims()
    return render_headline(claims, FIGURE_PATH)


if __name__ == "__main__":
    print(run())
