from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v134hb_commercial_aerospace_derivation_boundary_classification_audit_v1 import (
    V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Analyzer,
)


def test_v134hb_derivation_boundary_classification_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134HBCommercialAerospaceDerivationBoundaryClassificationAuditV1Analyzer(repo_root).analyze()

    assert result.summary["orders_last_trade_date"] == "20260227"
    assert result.summary["grouped_actions_last_trade_date"] == "20260227"
    assert result.summary["daily_state_last_trade_date"] == "20260320"
    assert result.summary["phase_table_last_trade_date"] == "20260320"
    assert result.summary["raw_daily_last_trade_date"] == "20260403"
    assert result.summary["raw_intraday_last_trade_date"] == "20260403"
    assert result.summary["lockout_end_trade_date"] == "20260320"
    assert result.summary["derived_stop_matches_lockout_end"] is True
    assert result.summary["derived_stop_after_last_execution"] is True
    assert result.summary["raw_coverage_beyond_derived"] is True
    assert result.summary["boundary_classification"] == "lockout_aligned_derivation_boundary"

    report_path = repo_root / "reports" / "analysis" / "v134hb_commercial_aerospace_derivation_boundary_classification_audit_v1.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
