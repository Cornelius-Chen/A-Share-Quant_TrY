from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gv_commercial_aerospace_reentry_unlock_handoff_readiness_audit_v1 import (
    V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Analyzer,
)
from a_share_quant.strategy.v134gw_commercial_aerospace_gv_handoff_direction_triage_v1 import (
    V134GWCommercialAerospaceGVHandoffDirectionTriageV1Analyzer,
)


def test_v134gw_handoff_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134gv_commercial_aerospace_reentry_unlock_handoff_readiness_audit_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GWCommercialAerospaceGVHandoffDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["seed_count"] == 3
    assert result.summary["handoff_ready_count"] == 0
    assert result.summary["lockout_overlap_block_count"] == 3
    assert result.summary["no_future_unlock_seed_count"] == 3

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["handoff_readiness_surface"]["status"] == "retain"
    assert rows["lockout_overlap_block"]["status"] == "dominant_blocker"
    assert rows["future_unlock_absence"]["status"] == "dominant_blocker"
    assert rows["add_handoff"]["status"] == "keep_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134gw_commercial_aerospace_gv_handoff_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
