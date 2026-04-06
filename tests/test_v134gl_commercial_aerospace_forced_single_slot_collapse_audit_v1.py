from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gl_commercial_aerospace_forced_single_slot_collapse_audit_v1 import (
    V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Analyzer,
)


def test_v134gl_forced_single_slot_collapse_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GLCommercialAerospaceForcedSingleSlotCollapseAuditV1Analyzer(repo_root).analyze()

    assert result.summary["preferred_surrogate_slot"] == "reset_slot"
    assert result.summary["preferred_surrogate_symbol"] == "002085"
    assert result.summary["reset_higher_metric_count"] == 3
    assert result.summary["continuation_higher_metric_count"] == 1

    by_state = {row["collapse_state"]: row for row in result.collapse_rows}
    assert by_state["forced_one_slot_local_reading"]["preferred_slot"] == "reset_slot"
    assert by_state["continuation_slot_counterfactual"]["preferred_slot"] == "continuation_slot"

    report_path = (
        repo_root / "reports" / "analysis" / "v134gl_commercial_aerospace_forced_single_slot_collapse_audit_v1.json"
    )
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
