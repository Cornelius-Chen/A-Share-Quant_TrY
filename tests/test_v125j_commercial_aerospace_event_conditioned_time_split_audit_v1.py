from pathlib import Path

from a_share_quant.strategy.v125j_commercial_aerospace_event_conditioned_time_split_audit_v1 import (
    V125JCommercialAerospaceEventConditionedTimeSplitAuditAnalyzer,
)


def test_v125j_reports_three_year_splits() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125JCommercialAerospaceEventConditionedTimeSplitAuditAnalyzer(repo_root).analyze()
    assert result.summary["year_count"] >= 3
