from pathlib import Path

from a_share_quant.strategy.v131n_commercial_aerospace_mn_5min_direction_triage_v1 import (
    V131NCommercialAerospaceMN5MinDirectionTriageAnalyzer,
)


def test_v131n_commercial_aerospace_mn_5min_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131NCommercialAerospaceMN5MinDirectionTriageAnalyzer(repo_root).analyze()

    assert result.summary["attempt_count"] == 4
    assert result.summary["authoritative_status"] in {
        "commercial_aerospace_5min_override_branch_unblocked",
        "commercial_aerospace_5min_override_branch_partially_ready_but_still_governed",
        "keep_commercial_aerospace_5min_branch_blocked",
    }
