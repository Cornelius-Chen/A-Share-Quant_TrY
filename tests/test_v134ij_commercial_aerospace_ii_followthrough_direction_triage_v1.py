from pathlib import Path

from a_share_quant.strategy.v134ij_commercial_aerospace_ii_followthrough_direction_triage_v1 import (
    V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Analyzer,
)


def test_v134ij_followthrough_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IJCommercialAerospaceIIFollowthroughDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["symbol_count"] == 4
    assert report.summary["persistent_followthrough_count"] == 1
    directions = {row["followthrough_label"]: row["direction"] for row in report.triage_rows}
    assert directions["persistent_symbol_followthrough_without_board_unlock"] == "retain_as_symbol_level_persistence_not_true_selection"
    assert directions["capital_true_selection"] == "continue_blocked_even_after_followthrough_surface_exists"
