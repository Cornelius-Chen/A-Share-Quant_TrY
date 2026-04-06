from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ji_commercial_aerospace_broader_attention_evidence_frontier_opening_v1 import (
    V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Analyzer,
)


def test_v134ji_broader_attention_evidence_frontier_opening() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JICommercialAerospaceBroaderAttentionEvidenceFrontierOpeningV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_name"] == "broader_attention_evidence"
    assert result.summary["frontier_state"] == "opened_protocol_only"
    assert result.summary["protocol_open_count"] == 3
    assert result.summary["deferred_component_count"] == 1
    assert result.summary["execution_blocked"] is True

    by_component = {row["component"]: row for row in result.frontier_rows}
    assert by_component["board_local_event_attention_capital_route"]["status"] == "frozen_input"
    assert by_component["capital_true_selection"]["status"] == "still_blocked"
