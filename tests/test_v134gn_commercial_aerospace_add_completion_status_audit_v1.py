from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gn_commercial_aerospace_add_completion_status_audit_v1 import (
    V134GNCommercialAerospaceAddCompletionStatusAuditV1Analyzer,
)


def test_v134gn_add_completion_status_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GNCommercialAerospaceAddCompletionStatusAuditV1Analyzer(repo_root).analyze()

    assert result.summary["seed_row_count"] == 55
    assert result.summary["seed_rule_match_rate"] == 1.0
    assert result.summary["observed_single_slot_day_count"] == 0
    assert result.summary["frozen_complete_count"] == 2
    assert result.summary["local_only_count"] == 3
    assert result.summary["blocked_count"] == 3

    rows = {row["component"]: row for row in result.component_rows}
    assert rows["seed_registry"]["status"] == "frozen_complete"
    assert rows["broader_positive_portability"]["status"] == "blocked"
    assert rows["portable_single_slot_template"]["status"] == "still_unobserved"
    assert rows["add_execution_authority"]["status"] == "still_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134gn_commercial_aerospace_add_completion_status_audit_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
