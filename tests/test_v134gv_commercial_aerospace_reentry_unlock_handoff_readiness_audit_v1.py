from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gv_commercial_aerospace_reentry_unlock_handoff_readiness_audit_v1 import (
    V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Analyzer,
)


def test_v134gv_handoff_readiness_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GVCommercialAerospaceReentryUnlockHandoffReadinessAuditV1Analyzer(repo_root).analyze()

    assert result.summary["seed_count"] == 3
    assert result.summary["handoff_ready_count"] == 0
    assert result.summary["lockout_overlap_block_count"] == 3
    assert result.summary["no_future_unlock_seed_count"] == 3

    by_symbol = {row["symbol"]: row for row in result.readiness_rows}
    assert by_symbol["000738"]["rebuild_watch_trade_date"] == "20260120"
    assert by_symbol["300342"]["rebuild_watch_trade_date"] == "20260123"
    assert by_symbol["688523"]["rebuild_watch_trade_date"] == "20260123"
    assert by_symbol["000738"]["handoff_ready"] is False
    assert "lockout_overlap_block" in by_symbol["000738"]["blocker_family"]
    assert "no_future_unlock_seed" in by_symbol["300342"]["blocker_family"]

    report_path = repo_root / "reports" / "analysis" / "v134gv_commercial_aerospace_reentry_unlock_handoff_readiness_audit_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
