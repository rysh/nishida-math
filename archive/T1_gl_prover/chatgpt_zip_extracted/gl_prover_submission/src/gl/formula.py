from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping, TypeAlias

FormulaJSON: TypeAlias = dict[str, Any]
Status: TypeAlias = Literal["proved", "refuted"]


@dataclass(frozen=True, slots=True)
class Formula:
    """Immutable syntax tree for the shared Formula JSON format."""

    type: str
    name: str | None = None
    arg: "Formula | None" = None
    args: tuple["Formula", ...] = ()
    left: "Formula | None" = None
    right: "Formula | None" = None

    def to_json(self) -> FormulaJSON:
        t = self.type
        if t == "bot":
            return {"type": "bot"}
        if t == "atom":
            assert self.name is not None
            return {"type": "atom", "name": self.name}
        if t in {"not", "box"}:
            assert self.arg is not None
            return {"type": t, "arg": self.arg.to_json()}
        if t in {"and", "or"}:
            return {"type": t, "args": [a.to_json() for a in self.args]}
        if t in {"imp", "iff"}:
            assert self.left is not None and self.right is not None
            return {"type": t, "left": self.left.to_json(), "right": self.right.to_json()}
        raise ValueError(f"unknown formula type: {t!r}")

    @staticmethod
    def from_json(data: Mapping[str, Any]) -> "Formula":
        t = data.get("type")
        if t == "bot":
            return bot()
        if t == "atom":
            name = data.get("name")
            if not isinstance(name, str) or not name:
                raise ValueError("atom formula requires a non-empty string name")
            return atom(name)
        if t == "not":
            return Not(Formula.from_json(_expect_mapping(data, "arg")))
        if t == "box":
            return Box(Formula.from_json(_expect_mapping(data, "arg")))
        if t == "and":
            return And(*(Formula.from_json(x) for x in _expect_list(data, "args")))
        if t == "or":
            return Or(*(Formula.from_json(x) for x in _expect_list(data, "args")))
        if t == "imp":
            return Imp(
                Formula.from_json(_expect_mapping(data, "left")),
                Formula.from_json(_expect_mapping(data, "right")),
            )
        if t == "iff":
            return Iff(
                Formula.from_json(_expect_mapping(data, "left")),
                Formula.from_json(_expect_mapping(data, "right")),
            )
        raise ValueError(f"unknown formula type: {t!r}")

    def __str__(self) -> str:
        return pretty(self)


@dataclass(frozen=True, slots=True)
class ProofResult:
    status: Status
    certificate: dict[str, Any] | None = None
    countermodel: dict[str, Any] | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "certificate": self.certificate,
            "countermodel": self.countermodel,
        }


def _expect_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"{key!r} must be a formula object")
    return value


def _expect_list(data: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(x, Mapping) for x in value):
        raise ValueError(f"{key!r} must be a list of formula objects")
    return value


def bot() -> Formula:
    return Formula("bot")


def atom(name: str) -> Formula:
    if not isinstance(name, str) or not name:
        raise ValueError("atom name must be a non-empty string")
    return Formula("atom", name=name)


def Not(arg: Formula) -> Formula:
    return Formula("not", arg=arg)


def And(*args: Formula) -> Formula:
    return Formula("and", args=tuple(args))


def Or(*args: Formula) -> Formula:
    return Formula("or", args=tuple(args))


def Imp(left: Formula, right: Formula) -> Formula:
    return Formula("imp", left=left, right=right)


def Iff(left: Formula, right: Formula) -> Formula:
    return Formula("iff", left=left, right=right)


def Box(arg: Formula) -> Formula:
    return Formula("box", arg=arg)


def negate(arg: Formula) -> Formula:
    if arg.type == "not" and arg.arg is not None:
        return arg.arg
    return Not(arg)


def box_power(arg: Formula, exponent: int) -> Formula:
    if exponent < 0:
        raise ValueError("box exponent must be non-negative")
    out = arg
    for _ in range(exponent):
        out = Box(out)
    return out


def con(n: int) -> Formula:
    """Con_n ≡ ¬□^(n+1)⊥.  The +1 is intentional."""
    if n < 0:
        raise ValueError("Con index must be non-negative")
    return Not(box_power(bot(), n + 1))


def modal_depth(f: Formula) -> int:
    t = f.type
    if t in {"bot", "atom"}:
        return 0
    if t == "not":
        assert f.arg is not None
        return modal_depth(f.arg)
    if t == "box":
        assert f.arg is not None
        return 1 + modal_depth(f.arg)
    if t in {"and", "or"}:
        return max((modal_depth(a) for a in f.args), default=0)
    if t in {"imp", "iff"}:
        assert f.left is not None and f.right is not None
        return max(modal_depth(f.left), modal_depth(f.right))
    raise ValueError(f"unknown formula type: {t!r}")


def atoms(f: Formula) -> frozenset[str]:
    t = f.type
    if t == "bot":
        return frozenset()
    if t == "atom":
        assert f.name is not None
        return frozenset({f.name})
    if t in {"not", "box"}:
        assert f.arg is not None
        return atoms(f.arg)
    if t in {"and", "or"}:
        out: set[str] = set()
        for a in f.args:
            out.update(atoms(a))
        return frozenset(out)
    if t in {"imp", "iff"}:
        assert f.left is not None and f.right is not None
        return atoms(f.left) | atoms(f.right)
    raise ValueError(f"unknown formula type: {t!r}")


def subformulas(f: Formula) -> frozenset[Formula]:
    out: set[Formula] = {f}
    t = f.type
    if t in {"not", "box"}:
        assert f.arg is not None
        out.update(subformulas(f.arg))
    elif t in {"and", "or"}:
        for a in f.args:
            out.update(subformulas(a))
    elif t in {"imp", "iff"}:
        assert f.left is not None and f.right is not None
        out.update(subformulas(f.left))
        out.update(subformulas(f.right))
    elif t in {"bot", "atom"}:
        pass
    else:
        raise ValueError(f"unknown formula type: {t!r}")
    return frozenset(out)


def modal_subformulas(f: Formula) -> frozenset[Formula]:
    return frozenset(s for s in subformulas(f) if s.type == "box")


def count_nodes(f: Formula) -> int:
    t = f.type
    if t in {"bot", "atom"}:
        return 1
    if t in {"not", "box"}:
        assert f.arg is not None
        return 1 + count_nodes(f.arg)
    if t in {"and", "or"}:
        return 1 + sum(count_nodes(a) for a in f.args)
    if t in {"imp", "iff"}:
        assert f.left is not None and f.right is not None
        return 1 + count_nodes(f.left) + count_nodes(f.right)
    raise ValueError(f"unknown formula type: {t!r}")


def eval_formula(f: Formula, model: Mapping[str, Any], world: int) -> bool:
    """Standard Kripke truth definition for Formula objects."""
    rel = {(int(a), int(b)) for a, b in model.get("rel", [])}
    val_raw = model.get("val", {})
    val = {str(name): {int(w) for w in worlds} for name, worlds in val_raw.items()}

    def ev(g: Formula, w: int) -> bool:
        t = g.type
        if t == "bot":
            return False
        if t == "atom":
            assert g.name is not None
            return w in val.get(g.name, set())
        if t == "not":
            assert g.arg is not None
            return not ev(g.arg, w)
        if t == "and":
            return all(ev(a, w) for a in g.args)
        if t == "or":
            return any(ev(a, w) for a in g.args)
        if t == "imp":
            assert g.left is not None and g.right is not None
            return (not ev(g.left, w)) or ev(g.right, w)
        if t == "iff":
            assert g.left is not None and g.right is not None
            return ev(g.left, w) == ev(g.right, w)
        if t == "box":
            assert g.arg is not None
            return all(ev(g.arg, v) for x, v in rel if x == w)
        raise ValueError(f"unknown formula type: {t!r}")

    return ev(f, int(world))


def pretty(f: Formula) -> str:
    t = f.type
    if t == "bot":
        return "⊥"
    if t == "atom":
        assert f.name is not None
        return f.name
    if t == "not":
        assert f.arg is not None
        return f"¬{_paren(f.arg)}"
    if t == "box":
        assert f.arg is not None
        return f"□{_paren(f.arg)}"
    if t == "and":
        return "(" + " ∧ ".join(pretty(a) for a in f.args) + ")"
    if t == "or":
        return "(" + " ∨ ".join(pretty(a) for a in f.args) + ")"
    if t == "imp":
        assert f.left is not None and f.right is not None
        return f"({_paren(f.left)} → {_paren(f.right)})"
    if t == "iff":
        assert f.left is not None and f.right is not None
        return f"({_paren(f.left)} ↔ {_paren(f.right)})"
    return repr(f)


def _paren(f: Formula) -> str:
    if f.type in {"bot", "atom"}:
        return pretty(f)
    return pretty(f)


def ensure_formula(value: Formula | Mapping[str, Any]) -> Formula:
    if isinstance(value, Formula):
        return value
    if isinstance(value, Mapping):
        return Formula.from_json(value)
    raise TypeError("expected Formula or Formula JSON mapping")


__all__ = [
    "Formula",
    "FormulaJSON",
    "ProofResult",
    "Status",
    "And",
    "Box",
    "Iff",
    "Imp",
    "Not",
    "Or",
    "atom",
    "atoms",
    "bot",
    "box_power",
    "con",
    "count_nodes",
    "ensure_formula",
    "eval_formula",
    "modal_depth",
    "modal_subformulas",
    "negate",
    "pretty",
    "subformulas",
]
