from pathlib import Path

from a_share_quant.strategy.v134fa_commercial_aerospace_ez_add_permission_direction_triage_v1 import (
    V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Analyzer,
)


def test_v134fa_commercial_aerospace_ez_add_permission_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FACommercialAerospaceEZAddPermissionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "keep_positive_add_rules_seed_only_but_retain_point_in_time_permission_clues_as_local_supervision"
    )
    assert result.summary["best_high_confidence_scenario"] == "slow_unlock_high_role_plus_contained_burst15"
