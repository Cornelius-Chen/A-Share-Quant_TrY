from pathlib import Path

from a_share_quant.strategy.v130r_bk0808_600118_near_surface_watch_window_audit_v1 import (
    V130RBK0808600118NearSurfaceWatchWindowAuditAnalyzer,
)


def test_v130r_bk0808_600118_near_surface_watch_window_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130RBK0808600118NearSurfaceWatchWindowAuditAnalyzer(repo_root).analyze()

    assert result.summary["symbol"] == "600118"
    assert result.summary["near_surface_watch_day_count"] > 0
    assert result.summary["authoritative_status"] == "600118_has_real_near_surface_watch_windows_but_still_not_same_plane_support"
