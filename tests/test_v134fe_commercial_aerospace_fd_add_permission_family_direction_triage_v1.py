from pathlib import Path

from a_share_quant.strategy.v134fe_commercial_aerospace_fd_add_permission_family_direction_triage_v1 import (
    V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Analyzer,
)


def test_v134fe_commercial_aerospace_fd_add_permission_family_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FECommercialAerospaceFDAddPermissionFamilyDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_permission_families_as_local_supervision_and_do_not_promote_broad_positive_add_rules"
    )
