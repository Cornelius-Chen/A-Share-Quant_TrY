from pathlib import Path

from a_share_quant.strategy.v132b_commercial_aerospace_ab_minute_label_direction_triage_v1 import (
    V132BCommercialAerospaceABMinuteLabelDirectionTriageAnalyzer,
)


def test_v132b_minute_label_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132BCommercialAerospaceABMinuteLabelDirectionTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "freeze_minute_tiered_label_specification_and_shift_next_to_local_1min_seed_window_extraction"
    )
    assert result.summary["registry_row_count"] == 6
