from pathlib import Path

from a_share_quant.strategy.v134fi_commercial_aerospace_fh_persistent_quality_direction_triage_v1 import (
    V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Analyzer,
)


def test_v134fi_commercial_aerospace_fh_persistent_quality_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FICommercialAerospaceFHPersistentQualityDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_persistent_permission_quality_tiers_as_local_supervision_only"
    )
