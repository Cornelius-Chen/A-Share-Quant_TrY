from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134je_commercial_aerospace_event_attention_capital_local_completion_audit_v1 import (
    V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Analyzer,
)


def test_v134je_event_attention_capital_local_completion_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JECommercialAerospaceEventAttentionCapitalLocalCompletionAuditV1Analyzer(repo_root).analyze()

    assert result.summary["negative_environment_ready"] is True
    assert result.summary["event_attention_local_stack_ready"] is True
    assert result.summary["capital_true_selection_still_blocked"] is True
    assert result.summary["single_hard_heat_source_stopline"] is True
    assert result.summary["current_local_route_exhausted"] is True

    by_component = {row["component"]: row for row in result.status_rows}
    assert by_component["capital_true_selection"]["status"] == "still_blocked"
    assert by_component["symbol_named_hard_heat_source_inventory"]["status"] == "single_case_stopline"
