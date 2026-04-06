from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ba_commercial_aerospace_window_capital_mapping_diffusion_audit_v1 import (
    V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Analyzer,
)


def test_v135ba_window_capital_mapping_diffusion_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135BACommercialAerospaceWindowCapitalMappingDiffusionAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 3
    assert result.summary["covered_window_count"] == 1
    assert result.summary["negative_sample_ready_count"] == 1
    assert result.summary["not_tradable_count"] == 2
    assert result.summary["negative_net_flow_count"] == 3
