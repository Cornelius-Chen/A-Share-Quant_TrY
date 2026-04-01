import json
from pathlib import Path

from a_share_quant.strategy.v115p_cpo_intraday_timing_aware_overlay_replay_v1 import (
    V115PCpoIntradayTimingAwareOverlayReplayAnalyzer,
)


def test_v115p_timing_aware_overlay_replay_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115m_payload=json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8")),
        v115o_payload=json.loads((repo_root / "reports" / "analysis" / "v115o_cpo_intraday_strict_band_signal_timing_audit_v1.json").read_text(encoding="utf-8")),
    )

    summary = result.summary
    assert summary["acceptance_posture"] == "freeze_v115p_cpo_intraday_timing_aware_overlay_replay_v1"
    assert summary["candidate_only_overlay"] is True
    assert summary["timing_bucket_used"] == "intraday_same_session_next_30m_bar_open"
    assert summary["strict_overlay_order_count"] >= 1
    assert summary["overlay_total_transaction_cost"] > 0
    assert summary["baseline_final_equity"] > 0
    assert summary["timing_aware_overlay_final_equity"] > 0
    assert summary["baseline_max_drawdown"] >= 0
    assert summary["timing_aware_overlay_max_drawdown"] >= 0
    assert len(result.overlay_order_rows) == summary["strict_overlay_order_count"]


def test_v115p_overlay_rows_stay_same_session_buy_only() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115m_payload=json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8")),
        v115o_payload=json.loads((repo_root / "reports" / "analysis" / "v115o_cpo_intraday_strict_band_signal_timing_audit_v1.json").read_text(encoding="utf-8")),
    )

    assert all(row["action"] == "buy" for row in result.overlay_order_rows)
    assert all(row["timing_bucket"] == "intraday_same_session" for row in result.overlay_order_rows)
    assert all(
        row["signal_trade_date"] == row["execution_trade_date"] for row in result.overlay_order_rows
    )
