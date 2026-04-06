from pathlib import Path

from a_share_quant.strategy.v121e_cpo_close_context_narrowing_audit_v1 import (
    V121ECpoCloseContextNarrowingAuditAnalyzer,
)
from a_share_quant.strategy.v121f_cpo_close_context_time_split_audit_v1 import (
    V121FCpoCloseContextTimeSplitAuditAnalyzer,
)


def test_v121f_close_context_time_split_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    narrowing = V121ECpoCloseContextNarrowingAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    analyzer = V121FCpoCloseContextTimeSplitAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v121e_payload=narrowing.as_dict())
    assert result.summary["split_count"] == 3
