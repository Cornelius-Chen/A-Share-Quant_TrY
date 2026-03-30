from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v11_continuation_readiness import (
    V11ContinuationReadinessAnalyzer,
    write_v11_continuation_readiness_report,
)


def test_v11_continuation_readiness_prefers_new_suspect_batch_when_all_lanes_closed(
    tmp_path: Path,
) -> None:
    analyzer = V11ContinuationReadinessAnalyzer()
    result = analyzer.analyze(
        q2_acceptance={"summary": {"do_continue_q2_capture_replay": False}},
        q3_acceptance={"summary": {"do_continue_q3_drawdown_replay": False}},
        q4_acceptance={"summary": {"do_continue_q4_drawdown_replay": False}},
        context_a_acceptance={
            "summary": {
                "acceptance_posture": "close_conditioned_late_quality_branch_as_non_material"
            }
        },
        context_b_report={
            "summary": {
                "do_continue_context_feature_pack_b": False,
                "recommended_posture": "close_sector_heat_breadth_context_branch_as_sparse",
                "candidate_row_count": 1,
            }
        },
        u2_readiness={"summary": {"u2_ready": False}},
        specialist_alpha={
            "summary": {"top_specialist_by_opportunity_count": "theme_strict_quality_branch"},
            "specialist_summaries": [
                {"opportunity_count": 7},
                {"opportunity_count": 12},
            ],
        },
    )

    assert result.summary["all_market_v1_slices_closed"] is True
    assert result.summary["all_context_branches_closed"] is True
    assert result.summary["recommended_next_phase"] == (
        "pause_specialist_refinement_and_prepare_new_suspect_batch"
    )
    assert result.summary["do_continue_current_specialist_loop"] is False

    output_path = write_v11_continuation_readiness_report(
        reports_dir=tmp_path,
        report_name="v11_continuation_readiness_test",
        result=result,
    )
    assert output_path.exists()
