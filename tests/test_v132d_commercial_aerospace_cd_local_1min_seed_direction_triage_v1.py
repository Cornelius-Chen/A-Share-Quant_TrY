from pathlib import Path

from a_share_quant.strategy.v132d_commercial_aerospace_cd_local_1min_seed_direction_triage_v1 import (
    V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageAnalyzer,
)


def test_v132d_local_1min_seed_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132DCommercialAerospaceCDLocal1MinSeedDirectionTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "freeze_local_1min_seed_window_table_and_shift_next_to_minute_pattern_envelope_audit"
    )
    assert result.summary["seed_window_row_count"] == 360
