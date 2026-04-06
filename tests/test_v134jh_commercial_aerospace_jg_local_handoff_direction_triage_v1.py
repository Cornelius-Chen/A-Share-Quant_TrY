from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jh_commercial_aerospace_jg_local_handoff_direction_triage_v1 import (
    V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Analyzer,
)


def test_v134jh_local_handoff_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JHCommercialAerospaceJGLocalHandoffDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["future_handoff_ready"] is True
    assert result.summary["capital_true_selection_blocked"] is True
    assert (
        result.summary["authoritative_status"]
        == "freeze_board_local_event_attention_capital_route_and_wait_for_future_evidence_shift"
    )
