# tests/test_ladder.py
"""WP3 ladder manifest and figure tests.

These tests exercise the same code paths that produce
``experiments/wp3/artifacts/ladder_manifest.json`` and
``experiments/wp3/artifacts/ladder_figure.svg``. The ``experiments``
directory is not on ``pythonpath``, so we add it explicitly here; this
keeps build_countermodels / build_ladder / build_figure runnable as
standalone scripts while still being testable from pytest.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_WP3_DIR = _REPO_ROOT / "experiments" / "wp3"
if str(_WP3_DIR) not in sys.path:
    sys.path.insert(0, str(_WP3_DIR))

build_ladder = importlib.import_module("build_ladder")
build_figure = importlib.import_module("build_figure")


@pytest.fixture(scope="module")
def manifest() -> dict:
    """Build the ladder manifest fresh so tests do not depend on whatever is
    currently committed under ``experiments/wp3/artifacts/``."""
    return build_ladder.build_ladder_data(max_n=8, exhaustive_max=5)


def test_manifest_top_level_shape(manifest: dict) -> None:
    assert manifest["max_n"] == 8
    assert manifest["exhaustive_max"] == 5
    assert len(manifest["stages"]) == 9


@pytest.mark.parametrize("n", range(9))
def test_witness_world_count_is_n_plus_two(manifest: dict, n: int) -> None:
    record = manifest["stages"][n]
    assert record["stage"] == n
    assert record["witness_world_count"] == n + 2


@pytest.mark.parametrize("n", range(9))
def test_each_stage_has_certified_monotone_and_strict(manifest: dict, n: int) -> None:
    record = manifest["stages"][n]
    assert record["monotone_status"] == "proved"
    assert record["strict_status"] == "refuted"
    assert record["countermodel_verified"] is True


@pytest.mark.parametrize("n", range(6))
def test_minimality_exhaustively_confirmed_for_small_n(
    manifest: dict, n: int
) -> None:
    record = manifest["stages"][n]
    assert record["minimality_exhaustively_checked"] is True
    check = record["minimality_check"]
    assert check["ok"] is True
    assert check["frames_examined"] >= 1


@pytest.mark.parametrize("n", range(6, 9))
def test_minimality_not_exhaustively_checked_for_large_n(
    manifest: dict, n: int
) -> None:
    record = manifest["stages"][n]
    assert record["minimality_exhaustively_checked"] is False
    assert "minimality_check" not in record


def test_figure_render_is_deterministic(manifest: dict, tmp_path: Path) -> None:
    first = tmp_path / "ladder_first.svg"
    second = tmp_path / "ladder_second.svg"
    build_figure.render_ladder(manifest, first)
    build_figure.render_ladder(manifest, second)
    assert first.read_bytes() == second.read_bytes()
