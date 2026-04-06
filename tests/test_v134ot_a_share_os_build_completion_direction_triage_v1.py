from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ot_a_share_os_build_completion_direction_triage_v1 import (
    V134OTAShareOSBuildCompletionDirectionTriageV1Analyzer,
)


def test_information_center_build_completion_direction_triage_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OTAShareOSBuildCompletionDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["foundation_complete_count"] == 13
    assert result.summary["global_blocker_count"] == 7


def test_information_center_build_completion_direction_triage_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OTAShareOSBuildCompletionDirectionTriageV1Analyzer(repo_root).analyze()

    directions = {row["component"]: row["direction"] for row in result.triage_rows}
    assert directions["core_build"] == "treat_information_center_core_as_built_complete_enough"
    assert directions["source_side"] == "advance_only_via_manual_closure_not_via_more_registry_buildout"
