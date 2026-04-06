from pathlib import Path

from a_share_quant.strategy.v130v_transfer_program_governance_bundle_v1 import (
    V130VTransferProgramGovernanceBundleAnalyzer,
)


def test_v130v_transfer_program_governance_bundle_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130VTransferProgramGovernanceBundleAnalyzer(repo_root).analyze()

    assert result.summary["closest_candidate_sector_id"] == "BK0808"
    assert result.summary["decisive_watch_symbol"] == "600118"
    assert result.summary["reopen_ready_count"] == 0
    assert any(
        row["sector_id"] == "BK0808" and row["next_action_rule"] == "reopen_only_after_real_v6_same_plane_emergence_of_600118"
        for row in result.bundle_rows
    )
