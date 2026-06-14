.PHONY: install test artifacts verify all help

help:
	@echo "Targets:"
	@echo "  install    - uv sync (install Python deps from uv.lock)"
	@echo "  test       - uv run pytest -q"
	@echo "  artifacts  - regenerate all experiment artifacts (WP3, WP4, WP5)"
	@echo "  verify     - regenerate artifacts and assert no git diff (determinism)"
	@echo "  all        - install + test + verify (single-command full reproduction)"

install:
	uv sync

test:
	uv run pytest -q

artifacts:
	uv run python experiments/wp3/build_countermodels.py
	uv run python experiments/wp3/build_ladder.py
	uv run python experiments/wp3/build_figure.py
	uv run python experiments/wp4/e_b1_classical_explosion.py
	uv run python experiments/wp4/e_b2_lp_quarantine.py
	uv run python experiments/wp5/build_claims.py
	uv run python experiments/wp5/build_table.py
	uv run python experiments/wp5/build_figure.py

verify: artifacts
	git diff --exit-code

all: install test verify
