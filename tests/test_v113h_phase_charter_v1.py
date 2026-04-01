from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113h_phase_charter_v1 import (
    V113HPhaseCharterAnalyzer,
    load_json_report,
)


def test_v113h_phase_charter_opens_with_frozen_packaging_surface_and_core_leader() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113HPhaseCharterAnalyzer()
    result = analyzer.analyze(
        v112cw_payload=load_json_report(repo_root / "reports/analysis/v112cw_packaging_mainline_extension_status_freeze_v1.json"),
        v112cx_payload=load_json_report(repo_root / "reports/analysis/v112cx_core_leader_holding_veto_promotion_review_v1.json"),
        owner_approves_execution_transition=True,
    )

    assert result.summary["do_open_v113h_now"] is True
    assert result.summary["selected_program"] == "cpo_execution_decision_layer_transition"
