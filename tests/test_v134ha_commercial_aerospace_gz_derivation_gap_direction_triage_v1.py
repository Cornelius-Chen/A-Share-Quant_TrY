from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gz_commercial_aerospace_board_surface_derivation_gap_audit_v1 import (
    V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Analyzer,
)
from a_share_quant.strategy.v134ha_commercial_aerospace_gz_derivation_gap_direction_triage_v1 import (
    V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Analyzer,
)


def test_v134ha_derivation_gap_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Analyzer(repo_root).analyze()
    audit_path = repo_root / "reports" / "analysis" / "v134gz_commercial_aerospace_board_surface_derivation_gap_audit_v1.json"
    audit_path.write_text(json.dumps(audit.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    result = V134HACommercialAerospaceGZDerivationGapDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["post_lockout_raw_trade_date_count"] == 10
    assert result.summary["daily_post_lockout_gap_count"] == 10
    assert result.summary["phase_post_lockout_gap_count"] == 10
    assert result.summary["synchronized_surface_stop"] is True

    rows = {row["component"]: row for row in result.triage_rows}
    assert rows["raw_intraday_calendar"]["status"] == "retain"
    assert rows["daily_state_surface"]["status"] == "dominant_gap"
    assert rows["phase_geometry_surface"]["status"] == "dominant_gap"
    assert rows["synchronized_surface_stop"]["status"] == "retain_as_primary_reading"
    assert rows["reentry_to_add_handoff"]["status"] == "keep_blocked"

    report_path = repo_root / "reports" / "analysis" / "v134ha_commercial_aerospace_gz_derivation_gap_direction_triage_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
