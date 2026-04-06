from pathlib import Path

from a_share_quant.strategy.v128v_commercial_aerospace_intraday_collapse_override_triage_v1 import (
    V128VCommercialAerospaceIntradayCollapseOverrideTriageAnalyzer,
)


def test_v128v_commercial_aerospace_intraday_collapse_override_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128VCommercialAerospaceIntradayCollapseOverrideTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == "retain_supervision_only_not_replay_facing"
    assert len(result.retained_rows) == 1
