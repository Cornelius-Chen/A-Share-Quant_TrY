from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v116k_cpo_visible_only_shadow_heat_trim_review_v1 import (
    V116KCpoVisibleOnlyShadowHeatTrimReviewAnalyzer,
)


def test_v116k_shadow_heat_trim_review_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116KCpoVisibleOnlyShadowHeatTrimReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v114x_payload=json.loads((repo_root / "reports" / "analysis" / "v114x_cpo_probability_expectancy_sizing_framework_repaired_v1.json").read_text(encoding="utf-8")),
        v116j_payload=json.loads((repo_root / "reports" / "analysis" / "v116j_cpo_visible_only_broader_shadow_replay_v1.json").read_text(encoding="utf-8")),
    )
    assert result.summary["acceptance_posture"] == "freeze_v116k_cpo_visible_only_shadow_heat_trim_review_v1"
    assert result.summary["variant_count"] >= 3
    assert any(int(row["executed_order_count"]) > 0 for row in result.variant_rows)
