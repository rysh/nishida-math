from experiments.wp6.e_c1_lp_truth_predicate import (
    BASE_ATOMS,
    build_full_fragment,
    classical_liar_oscillation,
    iterate_to_fixed_point,
    make_kat_results,
    values_for_code_table,
    verify_inertness,
    verify_minimality_by_enumeration,
    verify_monotone_by_covers,
)


def test_kat_results_all_pass() -> None:
    kats = make_kat_results(depth=2)
    assert len(kats) == 10
    assert all(kat["passed"] for kat in kats)


def test_lp_and_sk_liar_values() -> None:
    table = build_full_fragment()
    lp, _ = iterate_to_fixed_point(table, "lp", BASE_ATOMS)
    sk, _ = iterate_to_fixed_point(table, "sk", BASE_ATOMS)
    assert values_for_code_table(table, lp, BASE_ATOMS)["liar"] == "b"
    assert values_for_code_table(table, sk, BASE_ATOMS)["liar"] == "n"


def test_truth_teller_values() -> None:
    table = build_full_fragment()
    lp, _ = iterate_to_fixed_point(table, "lp", BASE_ATOMS)
    sk, _ = iterate_to_fixed_point(table, "sk", BASE_ATOMS)
    assert values_for_code_table(table, lp, BASE_ATOMS)["truthteller"] == "b"
    assert values_for_code_table(table, sk, BASE_ATOMS)["truthteller"] == "n"


def test_lp_no_explosion_witness() -> None:
    table = build_full_fragment()
    lp, _ = iterate_to_fixed_point(table, "lp", BASE_ATOMS)
    vals = values_for_code_table(table, lp, BASE_ATOMS)
    assert vals["liar_and_not_liar"] == "b"
    assert vals["q"] == "f"


def test_inertness_for_liar_free_generated_fragment() -> None:
    assert verify_inertness("lp", depth=2)["passed"]
    assert verify_inertness("sk", depth=2)["passed"]


def test_monotonicity_by_cover_edges() -> None:
    table = build_full_fragment()
    assert verify_monotone_by_covers(table, "lp", BASE_ATOMS)["passed"]
    assert verify_monotone_by_covers(table, "sk", BASE_ATOMS)["passed"]


def test_minimality_by_full_state_enumeration() -> None:
    table = build_full_fragment()
    assert verify_minimality_by_enumeration(table, "lp", BASE_ATOMS)["minimality_passed"]
    assert verify_minimality_by_enumeration(table, "sk", BASE_ATOMS)["minimality_passed"]


def test_classical_liar_has_no_fixed_point() -> None:
    table = build_full_fragment()
    contrast = classical_liar_oscillation(table)
    assert contrast["fixed_point_count"] == 0
    assert contrast["liar_truth_sequence_from_empty"][:4] == [False, True, False, True]
