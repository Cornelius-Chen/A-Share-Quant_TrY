from pathlib import Path

from a_share_quant.strategy.v134ey_commercial_aerospace_ex_context_gating_direction_triage_v1 import (
    V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Analyzer,
)


def test_v134ey_commercial_aerospace_ex_context_gating_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EYCommercialAerospaceEXContextGatingDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "keep_positive_add_rules_seed_only_and_shift_next_to_point_in_time_add_permission_context_audit"
    )
    assert result.summary["best_scenario_name"] == "unlock_worthy_plus_high_role"
