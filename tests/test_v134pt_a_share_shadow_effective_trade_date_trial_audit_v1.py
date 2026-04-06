from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pt_a_share_shadow_effective_trade_date_trial_audit_v1 import (
    V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer,
)


def test_v134pt_shadow_effective_trade_date_trial_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer(repo_root).analyze()

    assert report.summary["baseline_missing_count"] == 3
    assert report.summary["trial_missing_count"] == 2
    assert report.summary["trial_improvement_count"] == 1
    assert report.summary["candidate_effective_trade_date"] == "2026-03-27"


def test_v134pt_shadow_effective_trade_date_trial_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PTAShareShadowEffectiveTradeDateTrialAuditV1Analyzer(repo_root).analyze()
    row = next(r for r in report.rows if r["slice_id"] == "slice_20260328_194152")

    assert row["trial_query_trade_date"] == "2026-03-27"
    assert row["trial_tradeable_context_state"] == "date_level_tradeable_context_bound_via_effective_trade_date"
