from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1 import (
    V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Analyzer,
)
from a_share_quant.strategy.v134gs_commercial_aerospace_gr_reentry_unlock_bridge_direction_triage_v1 import (
    V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Analyzer,
)


def test_v134gs_reentry_unlock_bridge_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    bridge = V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Analyzer(repo_root).analyze()
    bridge_path = repo_root / "reports" / "analysis" / "v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1.json"
    bridge_path.write_text(json.dumps(bridge.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GSCommercialAerospaceGRReentryUnlockBridgeDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["bridge_stage_count"] == 8
    assert result.summary["same_day_block_seed_count"] == 3
    assert result.summary["execution_authority"] == "still_blocked"

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["shadow_bridge_module"]["status"] == "approved_for_next_build"
    assert rows["same_day_reentry"]["status"] == "keep_blocked"
    assert rows["execution_authority"]["status"] == "still_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134gs_commercial_aerospace_gr_reentry_unlock_bridge_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
