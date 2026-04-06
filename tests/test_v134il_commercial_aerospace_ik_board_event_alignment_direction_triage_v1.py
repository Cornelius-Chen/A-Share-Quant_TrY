from pathlib import Path

from a_share_quant.strategy.v134il_commercial_aerospace_ik_board_event_alignment_direction_triage_v1 import (
    V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Analyzer,
)


def test_v134il_board_event_alignment_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ILCommercialAerospaceIKBoardEventAlignmentDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["event_seed_count"] == 6
    directions = {row["alignment_label"]: row["direction"] for row in report.triage_rows}
    assert directions["aligned_board_supportive_response"] == "retain_as_the_cleanest_positive_alignment_case"
    assert directions["capital_true_selection"] == "continue_blocked_even_after_alignment_layer_exists"
