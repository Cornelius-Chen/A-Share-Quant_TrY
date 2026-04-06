from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pw_a_share_pv_shadow_corrected_binding_direction_triage_v1 import (
    V134PWASharePVShadowCorrectedBindingDirectionTriageV1Analyzer,
)


def test_v134pw_shadow_corrected_binding_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PWASharePVShadowCorrectedBindingDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_corrected_binding_view_is_useful_for_replay_only_and_should_not_replace_base_binding"
    )


def test_v134pw_shadow_corrected_binding_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PWASharePVShadowCorrectedBindingDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["shadow_corrected_binding"]["direction"] == "retain_as_shadow_only_overlay_for_replay_rechecks"
