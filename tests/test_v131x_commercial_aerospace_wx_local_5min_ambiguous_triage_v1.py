from pathlib import Path

from a_share_quant.strategy.v131x_commercial_aerospace_wx_local_5min_ambiguous_triage_v1 import (
    V131XCommercialAerospaceWXLocal5MinAmbiguousTriageAnalyzer,
)


def test_v131x_local_5min_ambiguous_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131XCommercialAerospaceWXLocal5MinAmbiguousTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_all_flagged_ambiguous_hits_as_mild_override_watch_seeds"
    )
    assert result.summary["mild_override_watch_count"] == 2
