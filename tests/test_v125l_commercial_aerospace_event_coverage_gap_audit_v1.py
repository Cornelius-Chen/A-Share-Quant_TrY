from pathlib import Path

from a_share_quant.strategy.v125l_commercial_aerospace_event_coverage_gap_audit_v1 import (
    V125LCommercialAerospaceEventCoverageGapAuditAnalyzer,
)


def test_v125l_reports_zero_coverage_or_negative_tail_years() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125LCommercialAerospaceEventCoverageGapAuditAnalyzer(repo_root).analyze()
    assert result.summary["best_variant"] == "quality_event_gate"
