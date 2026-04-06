from pathlib import Path

from a_share_quant.strategy.v133p_commercial_aerospace_op_visibility_direction_triage_v1 import (
    V133PCommercialAerospaceOPVisibilityDirectionTriageAnalyzer,
)


def test_v133p_commercial_aerospace_op_visibility_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133PCommercialAerospaceOPVisibilityDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["protocol_phase_count"] == 3
    assert report.triage_rows[0]["status"] == "approved_for_implementation"
    assert report.triage_rows[1]["status"] == "blocked_until_phase_1_audit_passes"
