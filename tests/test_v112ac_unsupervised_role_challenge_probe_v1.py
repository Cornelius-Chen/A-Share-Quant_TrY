from pathlib import Path

from a_share_quant.strategy.v112ac_unsupervised_role_challenge_probe_v1 import (
    V112ACUnsupervisedRoleChallengeProbeAnalyzer,
    load_json_report,
)


def test_v112ac_unsupervised_probe_keeps_governance_closed() -> None:
    analyzer = V112ACUnsupervisedRoleChallengeProbeAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ac_phase_charter_v1.json")),
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
        labeling_review_payload=load_json_report(Path("reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json")),
    )
    assert result.summary["cluster_count"] == 4
    assert result.summary["formal_role_replacement_forbidden"] is True
    assert result.summary["formal_training_still_forbidden"] is True
    assert result.summary["supportive_cluster_count"] >= 1
    assert result.summary["challenging_cluster_count"] >= 1
