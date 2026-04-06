from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jj_commercial_aerospace_ji_broader_attention_direction_triage_v1 import (
    V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Analyzer,
)


def test_v134jj_broader_attention_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JJCommercialAerospaceJIBroaderAttentionDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_name"] == "broader_attention_evidence"
    assert result.summary["frontier_state"] == "opened_protocol_only"
    assert result.summary["execution_blocked"] is True
    assert (
        result.summary["authoritative_status"]
        == "retain_frozen_local_route_and_only_open_broader_attention_evidence_as_protocol_frontier"
    )
