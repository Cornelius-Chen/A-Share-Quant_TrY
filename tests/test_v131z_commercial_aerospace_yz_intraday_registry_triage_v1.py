from pathlib import Path

from a_share_quant.strategy.v131z_commercial_aerospace_yz_intraday_registry_triage_v1 import (
    V131ZCommercialAerospaceYZIntradayRegistryTriageAnalyzer,
)


def test_v131z_intraday_registry_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131ZCommercialAerospaceYZIntradayRegistryTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "freeze_commercial_aerospace_intraday_supervision_registry_and_shift_next_to_minute_tiered_label_specification"
    )
    assert result.summary["registry_row_count"] == 6
