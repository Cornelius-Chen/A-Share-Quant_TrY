from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.next_suspect_batch_design import (
    NextSuspectBatchDesignAnalyzer,
    write_next_suspect_batch_design_report,
)


def test_next_suspect_batch_design_prefers_missing_context_archetypes(tmp_path: Path) -> None:
    analyzer = NextSuspectBatchDesignAnalyzer()
    result = analyzer.analyze(
        context_audit={
            "slice_rows": [
                {
                    "dataset_name": "market_research_v1",
                    "slice_name": "2024_q2",
                    "slice_role": "capture",
                    "context_tags": ["theme_loaded", "concentrated_turnover", "narrow_sector"],
                },
                {
                    "dataset_name": "market_research_v1",
                    "slice_name": "2024_q3",
                    "slice_role": "drawdown",
                    "context_tags": ["theme_light", "balanced_turnover", "broad_sector"],
                },
                {
                    "dataset_name": "market_research_v1",
                    "slice_name": "2024_q4",
                    "slice_role": "drawdown",
                    "context_tags": ["theme_light", "concentrated_turnover", "narrow_sector"],
                },
            ]
        },
        continuation_readiness={
            "summary": {
                "do_continue_current_specialist_loop": False,
            }
        },
        specialist_alpha={
            "summary": {"top_specialist_by_opportunity_count": "theme_strict_quality_branch"}
        },
    )

    assert result.summary["current_loop_paused"] is True
    assert result.summary["recommended_batch_posture"] == "expand_by_missing_context_archetypes"
    assert result.summary["recommended_next_batch_name"] == "market_research_v2_seed"
    assert len(result.missing_archetypes) >= 1
    assert result.missing_archetypes[0]["priority"] == 1

    output_path = write_next_suspect_batch_design_report(
        reports_dir=tmp_path,
        report_name="next_suspect_batch_design_test",
        result=result,
    )
    assert output_path.exists()
