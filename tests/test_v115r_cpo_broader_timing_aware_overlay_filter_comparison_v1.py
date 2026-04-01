import json
from pathlib import Path

from a_share_quant.strategy.v115r_cpo_broader_timing_aware_overlay_filter_comparison_v1 import (
    V115RCpoBroaderTimingAwareOverlayFilterComparisonAnalyzer,
)


def test_v115r_broader_timing_aware_overlay_filter_comparison_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115RCpoBroaderTimingAwareOverlayFilterComparisonAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115q_payload=json.loads((repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8")),
    )

    summary = result.summary
    assert summary["acceptance_posture"] == "freeze_v115r_cpo_broader_timing_aware_overlay_filter_comparison_v1"
    assert summary["variant_count"] == 4
    assert summary["best_variant_by_equity"] is not None
    assert summary["cleanest_variant_by_drawdown"] is not None
    assert len(result.variant_rows) == 4
    assert all(row["executed_order_count"] >= 0 for row in result.variant_rows)
