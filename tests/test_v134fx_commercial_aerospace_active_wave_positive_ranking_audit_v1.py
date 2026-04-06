from pathlib import Path

from a_share_quant.strategy.v134fx_commercial_aerospace_active_wave_positive_ranking_audit_v1 import (
    V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Analyzer,
)


def test_v134fx_commercial_aerospace_active_wave_positive_ranking_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FXCommercialAerospaceActiveWavePositiveRankingAuditV1Analyzer(repo_root).analyze()

    assert result.summary["selected_candidate_count"] == 2
    assert result.summary["state_count"] == 2
    assert result.summary["metric_count"] == 4
    assert result.summary["same_symbol_higher_metric_count"] == 1
    assert result.summary["clean_reset_higher_metric_count"] == 2
