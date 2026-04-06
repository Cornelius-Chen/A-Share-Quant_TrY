from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1 import (
    V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Analyzer,
)


def test_v134gr_reentry_unlock_shadow_bridge_spec() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GRCommercialAerospaceReentryUnlockShadowBridgeSpecV1Analyzer(repo_root).analyze()

    assert result.summary["bridge_stage_count"] == 8
    assert result.summary["reentry_seed_count"] == 3
    assert result.summary["same_day_block_seed_count"] == 3
    assert result.summary["lockout_seed_count"] == 1
    assert result.summary["unlock_positive_day_count"] == 8
    assert result.summary["unlock_worthy_count"] == 8

    rows = {row["bridge_stage"]: row for row in result.bridge_rows}
    assert rows["same_day_reentry"]["status"] == "blocked"
    assert rows["rebuild_watch_entry"]["status"] == "seed_supervision_ready"
    assert rows["handoff_to_add"]["status"] == "read_only_permission_bridge"

    report_path = repo_root / "reports" / "analysis" / "v134gr_commercial_aerospace_reentry_unlock_shadow_bridge_spec_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
