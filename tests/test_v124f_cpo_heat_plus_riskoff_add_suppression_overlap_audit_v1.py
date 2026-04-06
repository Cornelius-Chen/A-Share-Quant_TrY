from pathlib import Path

from a_share_quant.strategy.v124f_cpo_heat_plus_riskoff_add_suppression_overlap_audit_v1 import (
    V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditAnalyzer,
)


def test_v124f_add_suppression_overlap_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124FCpoHeatPlusRiskoffAddSuppressionOverlapAuditAnalyzer(repo_root=repo_root).analyze()

    assert result.summary["overlay_exec_row_count"] > 0
    assert len(result.overlap_rows) == 3
