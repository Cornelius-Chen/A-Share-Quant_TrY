from pathlib import Path

from a_share_quant.strategy.v134fg_commercial_aerospace_ff_persistent_confirmation_direction_triage_v1 import (
    V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Analyzer,
)


def test_v134fg_commercial_aerospace_ff_persistent_confirmation_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FGCommercialAerospaceFFPersistentConfirmationDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_persistent_permission_confirmation_as_local_supervision_only"
    )
