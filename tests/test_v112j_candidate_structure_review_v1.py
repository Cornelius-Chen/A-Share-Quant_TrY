from pathlib import Path

from a_share_quant.strategy.v112j_candidate_structure_review_v1 import (
    V112JCandidateStructureReviewAnalyzer,
    load_json_report,
)


def test_v112j_candidate_structure_review_v1_limits_follow_up_to_high_level_consolidation() -> None:
    result = V112JCandidateStructureReviewAnalyzer().analyze(
        protocol_payload=load_json_report(Path("reports/analysis/v112i_label_refinement_review_protocol_v1.json")),
        bucketization_payload=load_json_report(Path("reports/analysis/v112h_hotspot_bucketization_v1.json")),
    )
    assert result.summary["formal_label_split_now"] is False
    assert result.summary["bounded_follow_up_stage"] == "high_level_consolidation"
    assert len(result.stage_review_rows) == 2

