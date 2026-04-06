from pathlib import Path

from a_share_quant.strategy.v134ic_commercial_aerospace_carrier_grade_evidence_gap_audit_v1 import (
    V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Analyzer,
)


def test_v134ic_carrier_grade_evidence_gap_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ICCommercialAerospaceCarrierGradeEvidenceGapAuditV1Analyzer(repo_root).analyze()

    assert report.summary["event_backed_attention_carrier_count"] == 1
    assert report.summary["hard_anchor_case_count"] == 1
    assert report.summary["hard_decoy_case_count"] == 1
    assert report.summary["active_gap_count"] == 4
    names = {row["gap_name"] for row in report.gap_rows}
    assert "second_event_backed_carrier_case_missing" in names
    assert "anchor_decoy_counterpanel_too_thin" in names
