from pathlib import Path

from a_share_quant.strategy.v130a_bk0480_aerospace_aviation_role_surface_refresh_v2 import (
    V130ABK0480AerospaceAviationRoleSurfaceRefreshAnalyzer,
)


def test_v130a_bk0480_aerospace_aviation_role_surface_refresh_v2() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130ABK0480AerospaceAviationRoleSurfaceRefreshAnalyzer(repo_root).analyze()

    assert result.summary["confirmation_count"] == 1
    assert result.summary["quarantine_count"] == 2
    role_labels = {row["symbol"]: row["role_label"] for row in result.role_rows}
    assert role_labels["600760"] == "local_confirmation_candidate"
    assert role_labels["000099"] == "reject_or_mirror_pending"
