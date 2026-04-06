from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1 import (
    V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Analyzer,
)
from a_share_quant.strategy.v134hg_commercial_aerospace_hf_boundary_extension_opening_triage_v1 import (
    V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Analyzer,
)


def test_v134hg_boundary_extension_opening_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134HFCommercialAerospaceShadowBoundaryExtensionOpeningChecklistV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134hf_commercial_aerospace_shadow_boundary_extension_opening_checklist_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134HGCommercialAerospaceHFBoundaryExtensionOpeningTriageV1Analyzer(repo_root).analyze()

    assert result.summary["opening_gate_count"] == 8
    assert result.summary["boundary_classification"] == "lockout_aligned_derivation_boundary"
    assert result.summary["current_policy"] == "retain_current_boundary"

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["boundary_extension_opening_checklist"]["status"] == "retain_as_prelaunch_protocol"
    assert rows["current_derivation_boundary"]["status"] == "keep_frozen"
    assert rows["implicit_extension_now"]["status"] == "blocked"

    report_path = repo_root / "reports" / "analysis" / "v134hg_commercial_aerospace_hf_boundary_extension_opening_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
