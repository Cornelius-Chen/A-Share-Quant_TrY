from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jb_commercial_aerospace_ja_source_hardness_direction_triage_v1 import (
    V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Analyzer,
)


def test_v134jb_source_hardness_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JBCommercialAerospaceJASourceHardnessDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["only_hard_anchor_symbol"] == "000547"
    assert result.summary["hard_anchor_grade_source_count"] == 1
    assert (
        result.summary["authoritative_status"]
        == "retain_source_hardness_stopline_and_keep_true_selection_blocked"
    )

    triage_by_component = {row["component"]: row for row in result.triage_rows}
    assert (
        triage_by_component["capital_true_selection"]["direction"]
        == "continue_blocked_because_source_hardness_is_still_single_case"
    )
