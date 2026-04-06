from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gz_commercial_aerospace_board_surface_derivation_gap_audit_v1 import (
    V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Analyzer,
)


def test_v134gz_board_surface_derivation_gap_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GZCommercialAerospaceBoardSurfaceDerivationGapAuditV1Analyzer(repo_root).analyze()

    assert result.summary["lockout_end_trade_date"] == "20260320"
    assert result.summary["raw_last_trade_date"] == "20260403"
    assert result.summary["daily_last_trade_date"] == "20260320"
    assert result.summary["phase_last_trade_date"] == "20260320"
    assert result.summary["post_lockout_raw_trade_date_count"] == 10
    assert result.summary["daily_post_lockout_gap_count"] == 10
    assert result.summary["phase_post_lockout_gap_count"] == 10
    assert result.summary["synchronized_surface_stop"] is True

    by_surface = {row["surface_name"]: row for row in result.gap_rows}
    assert by_surface["raw_intraday_calendar"]["stop_alignment"] == "continues_past_lockout_end"
    assert by_surface["daily_state_surface"]["stop_alignment"] == "stops_at_lockout_end"
    assert by_surface["phase_geometry_surface"]["stop_alignment"] == "stops_at_lockout_end"

    report_path = repo_root / "reports" / "analysis" / "v134gz_commercial_aerospace_board_surface_derivation_gap_audit_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
