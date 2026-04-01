import json
from pathlib import Path

from a_share_quant.strategy.v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1 import (
    V115NCpoIntradayStrictBandHeldPositionOverlayReplayAnalyzer,
)


def test_v115n_overlay_replay_runs_on_repaired_baseline() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115NCpoIntradayStrictBandHeldPositionOverlayReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115m_payload=json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8")),
    )

    summary = result.summary
    assert summary["acceptance_posture"] == "freeze_v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1"
    assert summary["candidate_only_overlay"] is True
    assert summary["strict_miss_day_count"] >= 1
    assert summary["strict_overlay_order_count"] >= 1
    assert summary["overlay_total_transaction_cost"] > 0
    assert summary["baseline_final_equity"] > 0
    assert summary["overlay_final_equity"] > 0
    assert summary["baseline_max_drawdown"] >= 0
    assert summary["overlay_max_drawdown"] >= 0
    assert len(result.overlay_order_rows) == summary["strict_overlay_order_count"]
    assert len(result.replay_day_rows) > 0


def test_v115n_overlay_replay_stays_held_position_only() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115NCpoIntradayStrictBandHeldPositionOverlayReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115m_payload=json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8")),
    )

    assert all(row["action"] == "buy" for row in result.overlay_order_rows)
    assert all(row["overlay_posture"] == "strict_held_position_add_only" for row in result.overlay_order_rows)
