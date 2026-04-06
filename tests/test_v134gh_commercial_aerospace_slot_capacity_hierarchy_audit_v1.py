from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1 import (
    V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Analyzer,
)


def test_v134gh_slot_capacity_hierarchy_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GHCommercialAerospaceSlotCapacityHierarchyAuditV1Analyzer(repo_root).analyze()

    assert result.summary["active_wave_day_count"] == 2
    assert result.summary["zero_slot_veto_day_count"] == 1
    assert result.summary["tiered_dual_slot_day_count"] == 1
    assert result.summary["single_slot_unobserved_day_count"] == 0

    by_state = {row["hierarchy_state"]: row for row in result.hierarchy_rows}
    assert by_state["zero_slot_veto_day"]["trade_date"] == "20251218"
    assert by_state["zero_slot_veto_day"]["primary_driver"] == "recent_reduce_residue_exclusion"
    assert by_state["tiered_dual_slot_day"]["trade_date"] == "20251219"
    assert "reset_weight=" in by_state["tiered_dual_slot_day"]["supporting_reading"]

    report_path = repo_root / "reports" / "analysis" / "v134gh_commercial_aerospace_slot_capacity_hierarchy_audit_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
