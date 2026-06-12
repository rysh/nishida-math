# experiments/wp3/build_countermodels.py
"""Generate strict countermodel artifacts for T3.

For each n, strict_n{n}.json is the minimal linear (n+2)-world
transitive, irreflexive GL frame refuting Con_n -> Con_{n+1} at world 0.
The relation is written with its transitive closure included explicitly:
i R j iff i < j.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gl.formula import bot, Box, Not, Imp


def Con(n: int):
    """Con_n by the recursive definition: Con_0 := ¬□⊥; Con_{n+1} := ¬□¬Con_n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))


def linear_transitive_rel(num_worlds: int) -> list[list[int]]:
    """Return the strict linear order i R j iff i < j, transitive closure included."""
    if num_worlds < 1:
        raise ValueError("num_worlds must be positive")
    return [[i, j] for i in range(num_worlds) for j in range(i + 1, num_worlds)]


def strict_countermodel(n: int) -> dict[str, Any]:
    """Build the model JSON for the counterexample to Con_n -> Con_{n+1}."""
    if n < 0:
        raise ValueError("n must be non-negative")

    num_worlds = n + 2
    formula = Imp(Con(n), Con(n + 1))
    return {
        "worlds": list(range(num_worlds)),
        "rel": linear_transitive_rel(num_worlds),
        "val": {},
        "refutes": {
            "formula": formula.to_json(),
            "at": 0,
        },
        "checks": {
            "transitive": True,
            "irreflexive": True,
        },
    }


def write_countermodels(output_dir: Path, max_n: int = 4) -> list[Path]:
    """Write strict_n0.json through strict_n{max_n}.json and return their paths."""
    if max_n < 0:
        raise ValueError("max_n must be non-negative")

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for n in range(max_n + 1):
        path = output_dir / f"strict_n{n}.json"
        path.write_text(
            json.dumps(strict_countermodel(n), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


if __name__ == "__main__":
    default_dir = Path(__file__).resolve().parent / "countermodels"
    for output_path in write_countermodels(default_dir, max_n=4):
        print(output_path)
