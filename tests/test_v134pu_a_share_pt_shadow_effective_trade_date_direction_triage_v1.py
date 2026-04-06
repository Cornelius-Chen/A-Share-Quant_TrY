from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pu_a_share_pt_shadow_effective_trade_date_direction_triage_v1 import (
    V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Analyzer,
)


def test_v134pu_shadow_effective_trade_date_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_effective_trade_date_trial_is_directionally_useful_but_must_remain_shadow_only"
    )


def test_v134pu_shadow_effective_trade_date_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PUASharePTShadowEffectiveTradeDateDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["trial_result"]["direction"].startswith("retain_the_trial_as_evidence")
    assert rows["scope_boundary"]["direction"].startswith("keep_effective_trade_date_logic_in_shadow_only_scope")
