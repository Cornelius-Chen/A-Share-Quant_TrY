from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1 import (
    V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Analyzer,
)


def test_v134hf_shadow_boundary_extension_opening_checklist() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Analyzer(repo_root).analyze()

    assert result.summary["boundary_classification"] == "lockout_aligned_derivation_boundary"
    assert result.summary["current_policy"] == "retain_current_boundary"
    assert result.summary["future_policy_option"] == "explicit_boundary_extension_for_shadow_only"
    assert result.summary["shadow_lane_state"] == "opened_protocol_only"
    assert result.summary["opening_gate_count"] == 8

    rows = {row["opening_gate"]: row for row in result.checklist_rows}
    assert rows["explicit_shadow_only_policy_shift"]["status"] == "mandatory"
    assert rows["dual_surface_extension_required"]["status"] == "mandatory"
    assert rows["unlock_quality_debate_deferred"]["status"] == "mandatory"
    assert rows["bridge_handoff_stays_blocked_during_prelaunch"]["status"] == "mandatory"

    report_path = repo_root / "reports" / "analysis" / "v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
