from pathlib import Path

from a_share_quant.strategy.v126k_commercial_aerospace_authoritative_research_protocol_v1 import (
    V126KCommercialAerospaceAuthoritativeResearchProtocolAnalyzer,
)


def test_v126k_protocol_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126KCommercialAerospaceAuthoritativeResearchProtocolAnalyzer(repo_root).analyze()
    assert result.summary["current_authoritative_stage"] == "two_layer_shadow_refinement"
    assert len(result.phase_rows) >= 6
