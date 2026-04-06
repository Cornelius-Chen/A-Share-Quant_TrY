from pathlib import Path

from a_share_quant.strategy.v127h_commercial_aerospace_ghi_primary_attribution_triage_v1 import (
    V127HCommercialAerospaceGHIPrimaryAttributionTriageAnalyzer,
)


def test_v127h_primary_attribution_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127HCommercialAerospaceGHIPrimaryAttributionTriageAnalyzer(repo_root).analyze()
    assert result.summary["authoritative_next_step"] == "symbol_phase_aware_derisk_budget"
    assert len(result.subagent_rows) == 3
