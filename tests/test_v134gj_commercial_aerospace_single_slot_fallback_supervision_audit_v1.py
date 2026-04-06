from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1 import (
    V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Analyzer,
)


def test_v134gj_single_slot_fallback_supervision_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GJCommercialAerospaceSingleSlotFallbackSupervisionAuditV1Analyzer(repo_root).analyze()

    assert result.summary["observed_single_slot_day_count"] == 0
    assert result.summary["weak_surrogate_count"] == 1
    assert result.summary["surrogate_slot_name"] == "reset_slot"
    assert result.summary["surrogate_symbol"] == "002085"

    by_state = {row["fallback_state"]: row for row in result.fallback_rows}
    assert by_state["observed_single_slot_fallback"]["status"] == "unobserved"
    assert by_state["forced_local_surrogate"]["slot_name"] == "reset_slot"
    assert by_state["continuation_slot_counterpart"]["slot_name"] == "continuation_slot"

    report_path = (
        repo_root / "reports" / "analysis" / "v134gj_commercial_aerospace_single_slot_fallback_supervision_audit_v1.json"
    )
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
