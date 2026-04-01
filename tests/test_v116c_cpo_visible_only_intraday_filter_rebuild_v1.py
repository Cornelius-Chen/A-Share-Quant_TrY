import json
from pathlib import Path

from a_share_quant.strategy.v116c_cpo_visible_only_intraday_filter_rebuild_v1 import (
    V116CCpoVisibleOnlyIntradayFilterRebuildAnalyzer,
)


def test_v116c_visible_only_intraday_filter_rebuild_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116CCpoVisibleOnlyIntradayFilterRebuildAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115q_payload=json.loads((repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8")),
    )

    summary = result.summary
    assert summary["acceptance_posture"] == "freeze_v116c_cpo_visible_only_intraday_filter_rebuild_v1"
    assert summary["variant_count"] == 5
    assert summary["best_variant_by_equity"] is not None
    assert summary["cleanest_variant_by_drawdown"] is not None
    assert len(result.variant_rows) == 5
