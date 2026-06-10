"""
Formula representation for GL prover.
Uses frozen dataclasses for hashability and immutability.
Supports JSON roundtrip as per shared data format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union, List, Dict, Any, Set, Tuple, Optional
import json


@dataclass(frozen=True)
class Atom:
    name: str

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Atom name must be non-empty string")


@dataclass(frozen=True)
class Not:
    arg: Formula


@dataclass(frozen=True)
class And:
    args: Tuple[Formula, ...]  # tuple for hashability

    def __post_init__(self):
        if len(self.args) < 2:
            raise ValueError("And requires at least 2 args")


@dataclass(frozen=True)
class Or:
    args: Tuple[Formula, ...]

    def __post_init__(self):
        if len(self.args) < 2:
            raise ValueError("Or requires at least 2 args")


@dataclass(frozen=True)
class Imp:
    left: Formula
    right: Formula


@dataclass(frozen=True)
class Iff:
    left: Formula
    right: Formula


@dataclass(frozen=True)
class Box:
    arg: Formula


Formula = Union[Atom, Not, And, Or, Imp, Iff, Box]


def to_json(f: Formula) -> Dict[str, Any]:
    """Convert Formula to the shared JSON format."""
    if isinstance(f, Atom):
        return {"type": "atom", "name": f.name}
    elif isinstance(f, Not):
        return {"type": "not", "arg": to_json(f.arg)}
    elif isinstance(f, And):
        return {"type": "and", "args": [to_json(a) for a in f.args]}
    elif isinstance(f, Or):
        return {"type": "or", "args": [to_json(a) for a in f.args]}
    elif isinstance(f, Imp):
        return {"type": "imp", "left": to_json(f.left), "right": to_json(f.right)}
    elif isinstance(f, Iff):
        return {"type": "iff", "left": to_json(f.left), "right": to_json(f.right)}
    elif isinstance(f, Box):
        return {"type": "box", "arg": to_json(f.arg)}
    else:
        raise TypeError(f"Unknown formula type: {type(f)}")


def from_json(d: Dict[str, Any]) -> Formula:
    """Parse Formula from shared JSON format."""
    t = d["type"]
    if t == "atom":
        return Atom(d["name"])
    elif t == "not":
        return Not(from_json(d["arg"]))
    elif t == "and":
        return And(tuple(from_json(a) for a in d["args"]))
    elif t == "or":
        return Or(tuple(from_json(a) for a in d["args"]))
    elif t == "imp":
        return Imp(from_json(d["left"]), from_json(d["right"]))
    elif t == "iff":
        return Iff(from_json(d["left"]), from_json(d["right"]))
    elif t == "box":
        return Box(from_json(d["arg"]))
    else:
        raise ValueError(f"Unknown formula type in JSON: {t}")


def modal_depth(f: Formula) -> int:
    """Compute modal nesting depth."""
    if isinstance(f, (Atom,)):
        return 0
    elif isinstance(f, (Not, Box)):
        return modal_depth(f.arg) + (1 if isinstance(f, Box) else 0)
    elif isinstance(f, (And, Or)):
        return max((modal_depth(a) for a in f.args), default=0)
    elif isinstance(f, (Imp, Iff)):
        return max(modal_depth(f.left), modal_depth(f.right))
    raise TypeError(f"Unknown formula: {f}")


def get_atoms(f: Formula) -> Set[str]:
    """Collect all atom names in the formula. Exclude special bot/top."""
    atoms: Set[str] = set()
    if isinstance(f, Atom):
        if f.name not in ("bot", "top"):
            atoms.add(f.name)
    elif isinstance(f, (Not, Box)):
        atoms |= get_atoms(f.arg)
    elif isinstance(f, (And, Or)):
        for a in f.args:
            atoms |= get_atoms(a)
    elif isinstance(f, (Imp, Iff)):
        atoms |= get_atoms(f.left) | get_atoms(f.right)
    return atoms


def get_subformulas(f: Formula) -> Set[Formula]:
    """Collect all subformulas (for filtration / evaluation)."""
    subs: Set[Formula] = {f}
    if isinstance(f, (Not, Box)):
        subs |= get_subformulas(f.arg)
    elif isinstance(f, (And, Or)):
        for a in f.args:
            subs |= get_subformulas(a)
    elif isinstance(f, (Imp, Iff)):
        subs |= get_subformulas(f.left) | get_subformulas(f.right)
    return subs


def pretty(f: Formula) -> str:
    """Human readable string."""
    if isinstance(f, Atom):
        return f.name
    elif isinstance(f, Not):
        return f"¬{pretty(f.arg)}"
    elif isinstance(f, And):
        return "(" + " ∧ ".join(pretty(a) for a in f.args) + ")"
    elif isinstance(f, Or):
        return "(" + " ∨ ".join(pretty(a) for a in f.args) + ")"
    elif isinstance(f, Imp):
        return f"({pretty(f.left)} → {pretty(f.right)})"
    elif isinstance(f, Iff):
        return f"({pretty(f.left)} ↔ {pretty(f.right)})"
    elif isinstance(f, Box):
        return f"□{pretty(f.arg)}"
    raise TypeError(f"Unknown: {f}")


def bot() -> Formula:
    """False constant: p ∧ ¬p for fresh p, but for simplicity use a convention or Atom('⊥') but to stay in language, we use a special."""
    # For convenience in Con definitions, we introduce a convention: use Atom('bot') as falsum.
    # But to keep pure, many impl use it. Here we allow 'bot' as special atom that is never true.
    return Atom("bot")


def neg(f: Formula) -> Formula:
    return Not(f)


def conj(*args: Formula) -> Formula:
    if len(args) == 0:
        return Atom("top")  # not standard, but for convenience
    if len(args) == 1:
        return args[0]
    return And(tuple(args))


def disj(*args: Formula) -> Formula:
    if len(args) == 0:
        return neg(Atom("top"))
    if len(args) == 1:
        return args[0]
    return Or(tuple(args))


def imp(left: Formula, right: Formula) -> Formula:
    return Imp(left, right)


def box(f: Formula) -> Formula:
    return Box(f)


def diamond(f: Formula) -> Formula:
    return neg(box(neg(f)))


# Helpers for Con_n : ¬ □^{n+1} ⊥
def con_n(n: int) -> Formula:
    """Con_n ≡ ¬□^{n+1} bot """
    f: Formula = bot()
    for _ in range(n + 1):
        f = box(f)
    return neg(f)


def make_lob() -> Formula:
    """□(□A → A) → □A   (schema, here with atom p)"""
    p = Atom("p")
    inner = imp(box(p), p)
    return imp(box(inner), box(p))


def make_4() -> Formula:
    """□p → □□p"""
    p = Atom("p")
    return imp(box(p), box(box(p)))


def make_con_monotone(n: int) -> Formula:
    """Con_{n+1} → Con_n"""
    return imp(con_n(n + 1), con_n(n))


def make_con_strict(n: int) -> Formula:
    """Con_n → Con_{n+1}   (refutable)"""
    return imp(con_n(n), con_n(n + 1))


if __name__ == "__main__":
    # quick test
    p = Atom("p")
    print(pretty(p))
    print(modal_depth(box(p)))
    print(to_json(box(imp(p, neg(p)))))
    f = from_json({"type": "box", "arg": {"type": "atom", "name": "q"}})
    print(pretty(f))
    print(get_atoms(con_n(2)))
