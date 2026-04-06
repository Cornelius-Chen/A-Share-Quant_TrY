from pathlib import Path

from a_share_quant.strategy.v127t_commercial_aerospace_stu_post_pressure_direction_triage_v1 import (
    V127TCommercialAerospaceSTUPostPressureDirectionTriageAnalyzer,
)


def test_v127t_post_pressure_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127TCommercialAerospaceSTUPostPressureDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_next_step"] == "window_specific_derisk_grammar_for_20260112_to_20260212"
    assert len(report.subagent_rows) == 3
