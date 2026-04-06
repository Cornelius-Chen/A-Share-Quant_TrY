from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1 import (
    V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Analyzer,
)
from a_share_quant.strategy.v134gy_commercial_aerospace_gx_unlock_vacancy_direction_triage_v1 import (
    V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Analyzer,
)


def test_v134gy_unlock_vacancy_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134GYCommercialAerospaceGXUnlockVacancyDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["post_lockout_trade_date_count"] == 10
    assert result.summary["derived_board_surface_present_count"] == 0
    assert result.summary["raw_only_vacancy_count"] == 10
    assert result.summary["post_lockout_unlock_positive_count"] == 0

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["post_lockout_raw_calendar"]["status"] == "retain"
    assert rows["derived_board_surface"]["status"] == "dominant_blocker"
    assert rows["unlock_context"]["status"] == "keep_absent"
    assert rows["reentry_to_add_handoff"]["status"] == "keep_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134gy_commercial_aerospace_gx_unlock_vacancy_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
