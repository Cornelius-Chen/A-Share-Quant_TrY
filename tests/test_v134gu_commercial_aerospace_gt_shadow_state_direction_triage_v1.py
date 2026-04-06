from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1 import (
    V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Analyzer,
)
from a_share_quant.strategy.v134gu_commercial_aerospace_gt_shadow_state_direction_triage_v1 import (
    V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Analyzer,
)


def test_v134gu_shadow_state_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    surface = V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Analyzer(repo_root).analyze()
    surface_path = repo_root / "reports" / "analysis" / "v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1.json"
    surface_path.write_text(json.dumps(surface.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GUCommercialAerospaceGTShadowStateDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["seed_count"] == 3
    assert result.summary["pre_lockout_seed_count"] == 1
    assert result.summary["in_lockout_seed_count"] == 2
    assert result.summary["current_add_handoff_ready_count"] == 0

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["shadow_state_surface"]["status"] == "approved_as_first_concrete_bridge_surface"
    assert rows["same_day_reentry"]["status"] == "keep_blocked"
    assert rows["add_handoff"]["status"] == "not_ready_yet"
    assert rows["execution_authority"]["status"] == "still_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134gu_commercial_aerospace_gt_shadow_state_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
