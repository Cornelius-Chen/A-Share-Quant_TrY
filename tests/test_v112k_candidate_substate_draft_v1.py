from pathlib import Path

from a_share_quant.strategy.v112k_candidate_substate_draft_v1 import (
    V112KCandidateSubstateDraftAnalyzer,
    load_json_report,
)


def test_v112k_candidate_substate_draft_v1_stays_review_only() -> None:
    result = V112KCandidateSubstateDraftAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112k_phase_charter_v1.json")),
        candidate_review_payload=load_json_report(Path("reports/analysis/v112j_candidate_structure_review_v1.json")),
        bucketization_payload=load_json_report(Path("reports/analysis/v112h_hotspot_bucketization_v1.json")),
    )
    assert result.summary["formal_label_split_now"] is False
    assert result.summary["candidate_substate_count"] >= 2

