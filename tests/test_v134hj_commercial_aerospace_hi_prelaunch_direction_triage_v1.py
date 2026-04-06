from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hi_commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1 import (
    V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Analyzer,
)
from a_share_quant.strategy.v134hj_commercial_aerospace_hi_prelaunch_direction_triage_v1 import (
    V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Analyzer,
)


def test_v134hj_shadow_boundary_extension_prelaunch_direction() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    card = V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Analyzer(repo_root).analyze()
    card_path = repo_root / "reports" / "analysis" / "v134hi_commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1.json"
    card_path.write_text(json.dumps(card.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134HJCommercialAerospaceHIPrelaunchDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_state"] == "deferred_prelaunch"
    assert result.summary["opening_gate_count"] == 8
    assert result.summary["ready_to_open_now"] is False
    assert result.summary["silent_opening_allowed"] is False

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["prelaunch_status_card"]["status"] == "retain"
    assert rows["frontier_opening_now"]["status"] == "blocked"
    assert rows["silent_opening"]["status"] == "forbidden"

    report_path = repo_root / "reports" / "analysis" / "v134hj_commercial_aerospace_hi_prelaunch_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
