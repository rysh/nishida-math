# experiments/wp3/build_figure.py
"""Render the WP3 "ladder" figure as an SVG.

The figure plots, for each stage ``n``, the *minimal witness world count*
required for a Kripke countermodel that refutes
``Con_n -> Con_{n+1}`` at the root. The theoretical value is ``n + 2``
and the manifest produced by ``build_ladder.py`` confirms this
empirically: stages with ``minimality_exhaustively_checked == true``
(n <= 4) are pinned by exhaustive search; stages above that rely on the
stored ``(n+2)``-chain countermodel together with the prover refutation.

The renderer goes out of its way to be deterministic so that the SVG
checked into git does not flap on every regeneration:

* a fixed matplotlib backend (``Agg``);
* an explicit ``svg.hashsalt`` so embedded element ids are stable;
* no timestamp / no metadata block (``"none"`` in ``rcParams``);
* a fixed figure size and DPI;
* integer ticks, deterministic colours, no system-dependent fonts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MANIFEST_PATH = ARTIFACT_DIR / "ladder_manifest.json"
FIGURE_PATH = ARTIFACT_DIR / "ladder_figure.svg"


def _load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_ladder(manifest: dict[str, Any], output_path: Path) -> Path:
    """Render the ladder plot to ``output_path`` as SVG and return the path."""
    stages = manifest["stages"]
    xs = [s["stage"] for s in stages]
    ys = [s["witness_world_count"] for s in stages]
    exhaustive = [s["minimality_exhaustively_checked"] for s in stages]

    # Deterministic SVG output: fixed salt for element ids and font as paths
    # so the result does not depend on locally-installed font files.
    plt.rcParams["svg.hashsalt"] = "wp3-ladder"
    plt.rcParams["svg.fonttype"] = "path"
    plt.rcParams["pdf.fonttype"] = 42

    fig, ax = plt.subplots(figsize=(6.0, 4.0), dpi=100)

    # Connecting line first so that the markers sit on top.
    ax.plot(xs, ys, color="#1f4f8a", linewidth=1.2, zorder=1)

    confirmed_xs = [x for x, ok in zip(xs, exhaustive) if ok]
    confirmed_ys = [y for y, ok in zip(ys, exhaustive) if ok]
    inferred_xs = [x for x, ok in zip(xs, exhaustive) if not ok]
    inferred_ys = [y for y, ok in zip(ys, exhaustive) if not ok]

    ax.scatter(
        confirmed_xs,
        confirmed_ys,
        s=60,
        facecolors="#1f4f8a",
        edgecolors="#1f4f8a",
        label="minimality verified by exhaustive search",
        zorder=2,
    )
    ax.scatter(
        inferred_xs,
        inferred_ys,
        s=60,
        facecolors="white",
        edgecolors="#1f4f8a",
        linewidths=1.2,
        label="minimality assumed (refutation certified, search not exhausted)",
        zorder=2,
    )

    ax.set_xlabel("stage n")
    ax.set_ylabel("minimal witness world count")
    ax.set_title("The ladder: each stage requires a strictly deeper frame")
    ax.set_xticks(xs)
    ax.set_yticks(range(min(ys), max(ys) + 1))
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper left", frameon=False, fontsize=8)

    fig.tight_layout()
    fig.savefig(
        output_path,
        format="svg",
        metadata={"Date": None, "Creator": None},
    )
    plt.close(fig)
    return output_path


def run() -> Path:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()
    return render_ladder(manifest, FIGURE_PATH)


if __name__ == "__main__":
    path = run()
    print(path)
