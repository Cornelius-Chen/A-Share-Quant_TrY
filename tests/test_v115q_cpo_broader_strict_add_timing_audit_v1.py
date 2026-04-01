import json
from pathlib import Path

from a_share_quant.strategy.v115q_cpo_broader_strict_add_timing_audit_v1 import (
    V115QCpoBroaderStrictAddTimingAuditAnalyzer,
)


def test_v115q_broader_strict_add_timing_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115QCpoBroaderStrictAddTimingAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    summary = result.summary
    assert summary["acceptance_posture"] == "freeze_v115q_cpo_broader_strict_add_timing_audit_v1"
    assert summary["strict_add_context_row_count"] >= 1
    assert summary["intraday_same_session_count"] >= 1
    assert summary["positive_expectancy_count"] >= 1
    assert len(result.timing_rows) == summary["strict_add_context_row_count"]
    assert len(result.checkpoint_rows) >= len(result.timing_rows)
