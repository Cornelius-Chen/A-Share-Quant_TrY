from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113r_cpo_full_board_daily_bar_proxy_completion_v1 import sina_symbol
from a_share_quant.strategy.v113s_cpo_training_start_readiness_review_v1 import (
    V113SCPOTrainingStartReadinessReviewAnalyzer,
    load_json_report,
)


def test_sina_symbol_market_prefix() -> None:
    assert sina_symbol("300757") == "sz300757"
    assert sina_symbol("688498") == "sh688498"
    assert sina_symbol("603083") == "sh603083"


def test_v113s_training_start_readiness_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113SCPOTrainingStartReadinessReviewAnalyzer()
    result = analyzer.analyze(
        v113q_payload=load_json_report(repo_root / "reports" / "analysis" / "v113q_cpo_training_material_readiness_audit_v1.json"),
        v113r_payload={
            "summary": {
                "acceptance_posture": "freeze_v113r_cpo_full_board_daily_bar_proxy_completion_v1",
                "cohort_symbol_count": 20,
                "proxy_completed_symbol_count": 20,
                "training_use_allowed": True,
                "execution_use_allowed": False,
            }
        },
    )
    assert result.summary["board_level_training_ready_now"] is True
    assert result.summary["execution_level_full_board_ready_now"] is False
