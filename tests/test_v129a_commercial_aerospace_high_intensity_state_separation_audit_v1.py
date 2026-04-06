from pathlib import Path

from a_share_quant.strategy.v129a_commercial_aerospace_high_intensity_state_separation_audit_v1 import (
    V129ACommercialAerospaceHighIntensityStateSeparationAuditAnalyzer,
)


def test_v129a_commercial_aerospace_high_intensity_state_separation_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129ACommercialAerospaceHighIntensityStateSeparationAuditAnalyzer(repo_root).analyze()

    assert result.summary["train_row_count"] > 0
    assert result.summary["test_row_count"] > 0
    assert len(result.audit_rows) == 3

