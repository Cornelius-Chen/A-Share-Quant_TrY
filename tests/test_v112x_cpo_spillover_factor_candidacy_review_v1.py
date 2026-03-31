from pathlib import Path

from a_share_quant.strategy.v112x_cpo_spillover_factor_candidacy_review_v1 import (
    V112XSpilloverFactorCandidacyReviewAnalyzer,
    load_json_report,
)


def test_v112x_factor_candidacy_review_keeps_two_bounded_candidates() -> None:
    analyzer = V112XSpilloverFactorCandidacyReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112x_phase_charter_v1.json")),
        spillover_payload=load_json_report(Path("reports/analysis/v112t_cpo_spillover_truth_check_v1.json")),
    )
    assert result.summary["bounded_spillover_factor_candidate_count"] == 2
    assert result.summary["weak_memory_only_row_count"] == 1
    assert result.factor_review_rows[0]["probe_mode"] == "bounded_black_box_sidecar_readout"
