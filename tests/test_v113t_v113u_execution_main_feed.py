from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113u_cpo_execution_main_feed_readiness_audit_v1 import (
    V113UCPOExecutionMainFeedReadinessAuditAnalyzer,
    load_json_report,
)


def test_v113u_execution_main_feed_readiness_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113UCPOExecutionMainFeedReadinessAuditAnalyzer()
    result = analyzer.analyze(
        repo_root=repo_root,
        v112aa_payload=load_json_report(repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json"),
        v113t_payload={
            "summary": {
                "acceptance_posture": "freeze_v113t_cpo_execution_main_feed_build_v1",
                "output_csv": "data/raw/daily_bars/sina_daily_bars_cpo_execution_main_feed_v1.csv",
            }
        },
        v113q_payload={
            "summary": {
                "t_plus_one_enabled": True,
            }
        },
    )
    assert isinstance(result.checks, list)
