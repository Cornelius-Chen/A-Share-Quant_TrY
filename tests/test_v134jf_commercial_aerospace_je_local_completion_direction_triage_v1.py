from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jf_commercial_aerospace_je_local_completion_direction_triage_v1 import (
    V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Analyzer,
)


def test_v134jf_local_completion_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JFCommercialAerospaceJELocalCompletionDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["current_local_route_exhausted"] is True
    assert result.summary["capital_true_selection_still_blocked"] is True
    assert (
        result.summary["authoritative_status"]
        == "freeze_event_attention_capital_local_route_and_do_not_drift_inside_same_local_inventory"
    )
