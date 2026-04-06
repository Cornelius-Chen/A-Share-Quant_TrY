from pathlib import Path

from a_share_quant.strategy.v126d_commercial_aerospace_score_direction_audit_v1 import (
    V126DCommercialAerospaceScoreDirectionAuditAnalyzer,
)


def test_v126d_runs_score_direction_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126DCommercialAerospaceScoreDirectionAuditAnalyzer(repo_root).analyze()
    assert "best_eligibility_direction" in result.summary
