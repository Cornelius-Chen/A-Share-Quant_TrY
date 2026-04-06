from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gn_commercial_aerospace_add_completion_status_audit_v1 import (
    V134GNCommercialAerospaceAddCompletionStatusAuditV1Analyzer,
)
from a_share_quant.strategy.v134go_commercial_aerospace_gn_add_completion_direction_triage_v1 import (
    V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Analyzer,
)


def test_v134go_add_completion_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134GNCommercialAerospaceAddCompletionStatusAuditV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134gn_commercial_aerospace_add_completion_status_audit_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GOCommercialAerospaceGNAddCompletionDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["frozen_complete_count"] == 2
    assert result.summary["local_only_count"] == 3
    assert result.summary["blocked_count"] == 3

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["seed_supervision_stack"]["status"] == "freeze_as_complete_enough"
    assert rows["broader_positive_promotion"]["status"] == "keep_blocked"
    assert rows["single_slot_template"]["status"] == "keep_blocked"
    assert rows["execution_authority"]["status"] == "keep_blocked"
    assert rows["future_work_posture"]["status"] == "shift_to_local_residue_maintenance"

    report_path = repo_root / "reports" / "analysis" / "v134go_commercial_aerospace_gn_add_completion_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
