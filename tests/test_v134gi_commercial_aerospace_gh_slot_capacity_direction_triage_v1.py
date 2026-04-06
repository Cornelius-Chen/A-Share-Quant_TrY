from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1 import (
    V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Analyzer,
)
from a_share_quant.strategy.v134gi_commercial_aerospace_gh_slot_capacity_direction_triage_v1 import (
    V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Analyzer,
)


def test_v134gi_slot_capacity_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GICommercialAerospaceGHSlotCapacityDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["active_wave_day_count"] == 2
    assert result.summary["zero_slot_veto_day_count"] == 1
    assert result.summary["tiered_dual_slot_day_count"] == 1
    assert result.summary["single_slot_unobserved_day_count"] == 0

    triage = {row["component"]: row for row in result.triage_rows}
    assert triage["zero_slot_veto"]["status"] == "retain"
    assert triage["tiered_dual_slot"]["status"] == "retain_as_local"
    assert triage["single_slot_fallback"]["status"] == "still_unobserved"
    assert triage["execution_allocation_rule"]["status"] == "still_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134gi_commercial_aerospace_gh_slot_capacity_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
