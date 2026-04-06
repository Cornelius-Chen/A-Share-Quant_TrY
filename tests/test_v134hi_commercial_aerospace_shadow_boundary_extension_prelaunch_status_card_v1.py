from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hi_commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1 import (
    V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Analyzer,
)


def test_v134hi_shadow_boundary_extension_prelaunch_status_card() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134HICommercialAerospaceShadowBoundaryExtensionPrelaunchStatusCardV1Analyzer(repo_root).analyze()

    assert result.summary["frontier_name"] == "shadow_boundary_extension"
    assert result.summary["frontier_state"] == "deferred_prelaunch"
    assert result.summary["opening_gate_count"] == 8
    assert result.summary["ready_to_open_now"] is False
    assert result.summary["silent_opening_allowed"] is False

    rows = {row["key"]: row["value"] for row in result.status_rows}
    assert rows["boundary_classification"] == "lockout_aligned_derivation_boundary"
    assert rows["current_policy"] == "retain_current_boundary"
    assert rows["future_policy_option"] == "explicit_boundary_extension_for_shadow_only"
    assert rows["execution_authority"] == "blocked"

    report_path = repo_root / "reports" / "analysis" / "v134hi_commercial_aerospace_shadow_boundary_extension_prelaunch_status_card_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
