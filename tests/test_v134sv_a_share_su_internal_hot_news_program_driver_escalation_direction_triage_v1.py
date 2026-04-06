from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sv_a_share_su_internal_hot_news_program_driver_escalation_direction_triage_v1 import (
    V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Analyzer,
)


def test_v134sv_driver_escalation_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["alert_row_count"] == 1
    assert "driver-escalation_alert" in report.summary["authoritative_status"]


def test_v134sv_driver_escalation_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SVAShareSUInternalHotNewsProgramDriverEscalationDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 4
