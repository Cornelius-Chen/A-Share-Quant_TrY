from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v122z_cpo_research_test_baseline_heat_guardrail_review_v1 import (
    V122ZCpoResearchTestBaselineHeatGuardrailReviewAnalyzer,
    write_report,
)


def test_v122z_cpo_research_test_baseline_heat_guardrail_review_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V122ZCpoResearchTestBaselineHeatGuardrailReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122z_cpo_research_test_baseline_heat_guardrail_review_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["variant_count"] == 4
