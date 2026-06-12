# experiments/wp3/build_countermodels.py
import json
from pathlib import Path
from gl.formula import bot, Box, Not, Imp

def Con(n: int):
    if n == 0:
        return Not(Box(bot()))
    return Not(Box(Not(Con(n - 1))))

def build_strict_countermodel(n: int) -> dict:
    num_worlds = n + 2
    worlds = list(range(num_worlds))
    rel = [[i, j] for i in range(num_worlds) for j in range(i + 1, num_worlds)]
    formula = Imp(Con(n), Con(n + 1))
    return {
        "worlds": worlds,
        "rel": rel,
        "val": {},
        "refutes": {"formula": formula.to_json(), "at": 0},
        "checks": {"transitive": True, "irreflexive": True},
    }

def main():
    out_dir = Path("experiments/wp3/countermodels")
    out_dir.mkdir(parents=True, exist_ok=True)
    for n in range(5):
        model = build_strict_countermodel(n)
        (out_dir / f"strict_n{n}.json").write_text(
            json.dumps(model, indent=2, ensure_ascii=False) + "
"
        )

if __name__ == "__main__":
    main()
