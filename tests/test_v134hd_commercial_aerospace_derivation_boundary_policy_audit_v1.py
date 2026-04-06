from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1 import (
    V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Analyzer,
)


def test_v134hd_derivation_boundary_policy_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134HDCommercialAerospaceDerivationBoundaryPolicyAuditV1Analyzer(repo_root).analyze()

    assert result.summary["boundary_classification"] == "lockout_aligned_derivation_boundary"
    assert result.summary["post_lockout_trade_date_count"] == 10
    assert result.summary["raw_only_vacancy_count"] == 10
    assert result.summary["shadow_lane_state"] == "opened_protocol_only"
    assert result.summary["current_policy"] == "retain_current_boundary"
    assert result.summary["future_policy_option"] == "explicit_boundary_extension_for_shadow_only"

    rows = {row["policy_option"]: row for row in result.policy_rows}
    assert rows["implicit_auto_extension_from_raw"]["status"] == "rejected"
    assert rows["explicit_boundary_extension_for_shadow_only"]["status"] == "deferred_until_explicit_shift"
    assert rows["retain_current_boundary"]["status"] == "current_authoritative"
    assert rows["unlock_classifier_debate_before_extension"]["status"] == "rejected_ordering"

    report_path = repo_root / "reports" / "analysis" / "v134hd_commercial_aerospace_derivation_boundary_policy_audit_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
