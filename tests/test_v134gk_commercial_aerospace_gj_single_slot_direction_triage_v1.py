from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1 import (
    V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Analyzer,
)
from a_share_quant.strategy.v134gk_commercial_aerospace_gj_single_slot_direction_triage_v1 import (
    V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Analyzer,
)


def test_v134gk_single_slot_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Analyzer(repo_root).analyze()
    audit_path = (
        repo_root / "reports" / "analysis" / "v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1.json"
    )
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GKCommercialAerospaceGJSingleSlotDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["observed_single_slot_day_count"] == 0
    assert result.summary["weak_surrogate_count"] == 1
    assert result.summary["surrogate_slot_name"] == "reset_slot"

    triage = {row["component"]: row for row in result.triage_rows}
    assert triage["observed_single_slot_fallback"]["status"] == "still_unobserved"
    assert triage["reset_slot_surrogate"]["status"] == "retain_as_weak_local_surrogate"
    assert triage["continuation_slot"]["status"] == "retain_as_companion_only"
    assert triage["execution_single_slot_rule"]["status"] == "still_blocked"

    report_path = (
        repo_root / "reports" / "analysis" / "v134gk_commercial_aerospace_gj_single_slot_direction_triage_v1.json"
    )
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
