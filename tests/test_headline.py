# tests/test_headline.py
"""WP5 headline manifest, table, and figure tests."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_WP5_DIR = _REPO_ROOT / "experiments" / "wp5"


def _load_module(name: str, path: Path) -> ModuleType:
    """Load a module by its file path under a unique name.

    The WP3 ``build_figure`` and the WP5 ``build_figure`` share the same
    base file name, so plain ``importlib.import_module("build_figure")``
    returns whichever one another test imported first. We register both
    under qualified names here.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_claims = _load_module("wp5_build_claims", _WP5_DIR / "build_claims.py")
build_table = _load_module("wp5_build_table", _WP5_DIR / "build_table.py")
build_figure = _load_module("wp5_build_figure", _WP5_DIR / "build_figure.py")


@pytest.fixture(scope="module")
def claims() -> dict:
    """Build the claims manifest fresh from the artifacts on disk so the
    tests do not silently rely on whatever is currently in
    ``claims.json``."""
    return build_claims.build_claims_data()


def test_claims_top_level_shape(claims: dict) -> None:
    assert "rows" in claims
    assert claims["columns"] == [
        "contradiction_status",
        "what_follows",
        "formal_witness",
        "generativity",
    ]
    environments = [r["environment"] for r in claims["rows"]]
    assert environments == [
        "Classical propositional logic",
        "LP (Priest's Logic of Paradox)",
        "GL (Gödel-Löb provability logic)",
    ]


def test_each_row_witness_artifact_exists(claims: dict) -> None:
    for row in claims["rows"]:
        primary = _REPO_ROOT / row["formal_witness"]["artifact"]
        assert primary.is_file(), f"missing artifact: {primary}"
        details = row["formal_witness"].get("details_artifact")
        if details is not None:
            assert (_REPO_ROOT / details).is_file(), f"missing details: {details}"


def test_classical_row_matches_artifact(claims: dict) -> None:
    row = claims["rows"][0]
    artifact = json.loads(
        (_REPO_ROOT / row["formal_witness"]["artifact"]).read_text(encoding="utf-8")
    )
    keys = row["formal_witness"]["keys"]
    assert artifact["satisfiable"] is False
    assert keys["satisfiable"] is False
    assert artifact["vacuous_explosion"] is True
    assert keys["vacuous_explosion"] is True


def test_lp_row_matches_artifact(claims: dict) -> None:
    row = claims["rows"][1]
    artifact = json.loads(
        (_REPO_ROOT / row["formal_witness"]["artifact"]).read_text(encoding="utf-8")
    )
    keys = row["formal_witness"]["keys"]
    assert artifact["satisfiable"] is True
    assert artifact["inert"] is True
    assert artifact["mp_failure"] == keys["mp_failure"]
    assert artifact["ds_failure"] == keys["ds_failure"]


def test_gl_row_matches_artifact(claims: dict) -> None:
    row = claims["rows"][2]
    manifest = json.loads(
        (_REPO_ROOT / row["formal_witness"]["artifact"]).read_text(encoding="utf-8")
    )
    keys = row["formal_witness"]["keys"]
    assert manifest["max_n"] == keys["max_n"] == 8
    assert manifest["exhaustive_max"] == keys["exhaustive_max"] == 4
    counts = [s["witness_world_count"] for s in manifest["stages"]]
    assert counts == keys["witness_world_counts"] == list(range(2, 11))
    assert all(s["monotone_status"] == "proved" for s in manifest["stages"])
    assert all(s["strict_status"] == "refuted" for s in manifest["stages"])


def test_build_claims_rejects_drift(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """If an input artifact's key disagrees with the hardcoded expectation,
    ``build_claims_data`` must raise rather than silently writing a bad
    manifest."""
    bad_summary = tmp_path / "fake_e_b1.json"
    bad_summary.write_text(
        json.dumps(
            {"satisfiable": True, "vacuous_explosion": False, "enumeration_size": 2}
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(build_claims, "CLASSICAL_SUMMARY", bad_summary)
    with pytest.raises(AssertionError):
        build_claims.build_claims_data()


def test_table_markdown_mentions_all_environments(claims: dict) -> None:
    markdown = build_table.render_table(claims)
    for row in claims["rows"]:
        assert row["environment"] in markdown
        assert row["generativity"] in markdown
    # The reading legend describes the four columns explicitly.
    for column_name in [
        "Contradiction status",
        "What follows from the seed",
        "Formal witness",
        "Generativity",
    ]:
        assert column_name in markdown


def test_figure_render_is_deterministic(claims: dict, tmp_path: Path) -> None:
    first = tmp_path / "headline_first.svg"
    second = tmp_path / "headline_second.svg"
    build_figure.render_headline(claims, first)
    build_figure.render_headline(claims, second)
    assert first.read_bytes() == second.read_bytes()
