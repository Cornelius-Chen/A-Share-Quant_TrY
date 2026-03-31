from pathlib import Path

from a_share_quant.strategy.v112i_label_refinement_review_protocol_v1 import (
    V112ILabelRefinementReviewProtocolAnalyzer,
    load_json_report,
)


def test_v112i_label_refinement_review_protocol_v1_freezes_review_gates() -> None:
    result = V112ILabelRefinementReviewProtocolAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112i_phase_charter_v1.json")),
        refinement_design_payload=load_json_report(Path("reports/analysis/v112f_refinement_design_v1.json")),
        semantic_rerun_payload=load_json_report(Path("reports/analysis/v112g_phase_closure_check_v1.json")),
    )
    assert result.summary["acceptance_posture"] == "freeze_v112i_label_refinement_review_protocol_v1"
    assert result.summary["protocol_ready_for_candidate_structure_review"] is True
    assert len(result.review_gate_rows) == 3

