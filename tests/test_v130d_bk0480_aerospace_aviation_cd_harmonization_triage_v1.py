from pathlib import Path

from a_share_quant.strategy.v130d_bk0480_aerospace_aviation_cd_harmonization_triage_v1 import (
    V130DBK0480AerospaceAviationCDHarmonizationTriageAnalyzer,
)


def test_v130d_bk0480_aerospace_aviation_cd_harmonization_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130DBK0480AerospaceAviationCDHarmonizationTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "freeze_bk0480_role_surface_v2_and_block_wider_control_refresh_until_harmonization_exists"
    )
    assert any(row["direction"] == "replay_unlock" and row["status"] == "blocked" for row in result.direction_rows)
