from pathlib import Path

from a_share_quant.strategy.v130b_bk0480_aerospace_aviation_ab_role_surface_direction_triage_v1 import (
    V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageAnalyzer,
)


def test_v130b_bk0480_aerospace_aviation_ab_role_surface_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130BBK0480AerospaceAviationABRoleSurfaceDirectionTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "freeze_bk0480_role_surface_v2_and_move_to_control_surface_refresh_with_harmonization_guard"
    )
    assert any(row["direction"] == "replay_unlock" and row["status"] == "still_blocked" for row in result.direction_rows)
