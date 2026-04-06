from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1 import (
    V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Analyzer,
)


def test_v134gt_reentry_unlock_shadow_state_surface() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GTCommercialAerospaceReentryUnlockShadowStateSurfaceV1Analyzer(repo_root).analyze()

    assert result.summary["seed_count"] == 3
    assert result.summary["pre_lockout_seed_count"] == 1
    assert result.summary["in_lockout_seed_count"] == 2
    assert result.summary["current_add_handoff_ready_count"] == 0
    assert result.summary["same_day_block_seed_count"] == 3

    by_symbol = {row["symbol"]: row for row in result.state_rows}
    assert by_symbol["000738"]["board_gate_state"] == "pre_lockout_seed"
    assert by_symbol["300342"]["board_gate_state"] == "in_lockout_seed"
    assert by_symbol["688523"]["board_gate_state"] == "in_lockout_seed"
    assert by_symbol["000738"]["add_handoff_state"] == "blocked_until_board_unlock"

    report_path = repo_root / "reports" / "analysis" / "v134gt_commercial_aerospace_reentry_unlock_shadow_state_surface_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
