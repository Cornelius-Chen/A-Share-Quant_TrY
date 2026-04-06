from pathlib import Path

from a_share_quant.strategy.v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1 import (
    V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditAnalyzer,
)


def test_v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditAnalyzer(repo_root).analyze()

    assert result.summary["nearest_same_plane_watch"] == ["600118"]
    assert result.summary["historical_bridge_watch"] == ["600760"]
    assert result.summary["authoritative_status"] == "watch_bk0808_for_second_same_plane_symbol_but_do_not_unlock_worker"
