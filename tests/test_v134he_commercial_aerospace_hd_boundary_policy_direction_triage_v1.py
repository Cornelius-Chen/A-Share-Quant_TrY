from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1 import (
    V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Analyzer,
)
from a_share_quant.strategy.v134he_commercial_aerospace_hd_boundary_policy_direction_triage_v1 import (
    V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Analyzer,
)


def test_v134he_boundary_policy_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134HECommercialAerospaceHDBoundaryPolicyDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["boundary_classification"] == "lockout_aligned_derivation_boundary"
    assert result.summary["current_policy"] == "retain_current_boundary"
    assert result.summary["future_policy_option"] == "explicit_boundary_extension_for_shadow_only"

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["current_boundary"]["status"] == "retain"
    assert rows["implicit_auto_extension"]["status"] == "keep_rejected"
    assert rows["explicit_shadow_only_extension"]["status"] == "future_option_only"
    assert rows["unlock_quality_debate"]["status"] == "defer_until_boundary_changes"
    assert rows["shadow_bridge"]["status"] == "keep_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134he_commercial_aerospace_hd_boundary_policy_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
