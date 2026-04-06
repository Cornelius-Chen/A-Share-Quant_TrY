from pathlib import Path

from a_share_quant.strategy.v129z_bk0480_aerospace_aviation_yz_local_universe_triage_v1 import (
    V129ZBK0480AerospaceAviationYZLocalUniverseTriageAnalyzer,
)


def test_v129z_bk0480_aerospace_aviation_yz_local_universe_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129ZBK0480AerospaceAviationYZLocalUniverseTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "admit_600760_as_confirmation_only_keep_002273_601989_quarantined_and_reject_000099_for_now"
    )
    assert any(row["direction"] == "next_primary_direction" for row in result.direction_rows)
