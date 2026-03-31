from __future__ import annotations

from a_share_quant.strategy.v112g_phase_check_v1 import V112GPhaseCheckAnalyzer


def test_v112g_phase_check_reports_semantic_v2_success() -> None:
    result = V112GPhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112g_now": True}},
        feature_schema_payload={"summary": {"ready_for_baseline_v2_next": True, "new_feature_count": 3, "total_feature_count_v2": 15}},
        baseline_v2_payload={"summary": {"ready_for_gbdt_v2_next": True, "baseline_v2_test_accuracy": 0.47}},
        gbdt_v2_payload={"summary": {"ready_for_phase_check_next": True, "gbdt_v2_test_accuracy": 0.56, "gbdt_v2_high_level_consolidation_fp": 1}},
    )

    assert result.summary["feature_schema_v2_present"] is True
    assert result.summary["ready_for_phase_closure_next"] is True
