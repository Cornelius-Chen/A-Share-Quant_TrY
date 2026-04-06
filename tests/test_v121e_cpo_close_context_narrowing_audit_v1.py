from pathlib import Path

from a_share_quant.strategy.v121e_cpo_close_context_narrowing_audit_v1 import (
    V121ECpoCloseContextNarrowingAuditAnalyzer,
)


def test_v121e_close_context_narrowing_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121ECpoCloseContextNarrowingAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["close_context_row_count"] > 0
    assert result.summary["best_balanced_accuracy"] >= 0.0

