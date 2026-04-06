from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1 import (
    V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Analyzer,
)


def test_v134gx_post_lockout_unlock_vacancy_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GXCommercialAerospacePostLockoutUnlockVacancyAuditV1Analyzer(repo_root).analyze()

    assert result.summary["lockout_end_trade_date"] == "20260320"
    assert result.summary["post_lockout_trade_date_count"] == 10
    assert result.summary["derived_board_surface_present_count"] == 0
    assert result.summary["raw_only_vacancy_count"] == 10
    assert result.summary["post_lockout_unlock_positive_count"] == 0
    assert result.summary["post_lockout_unlock_worthy_count"] == 0

    first_row = result.vacancy_rows[0]
    last_row = result.vacancy_rows[-1]
    assert first_row["trade_date"] == "20260323"
    assert last_row["trade_date"] == "20260403"
    assert first_row["raw_intraday_present"] is True
    assert first_row["derived_board_surface_present"] is False
    assert first_row["vacancy_family"] == "raw_only_post_lockout_vacancy"
    assert last_row["vacancy_family"] == "raw_only_post_lockout_vacancy"

    report_path = repo_root / "reports" / "analysis" / "v134gx_commercial_aerospace_post_lockout_unlock_vacancy_audit_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
