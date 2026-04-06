from pathlib import Path

from a_share_quant.strategy.v127p_commercial_aerospace_opq_new_primary_direction_triage_v1 import (
    V127PCommercialAerospaceOPQNewPrimaryDirectionTriageAnalyzer,
)


def test_v127p_new_primary_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127PCommercialAerospaceOPQNewPrimaryDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_next_step"] == "new_primary_drawdown_window_attribution"
    assert len(report.subagent_rows) == 3
