from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v122a_cpo_xyz_1min_family_three_run_adversarial_triage_v1 import (
    V122ACpoXyz1MinFamilyThreeRunAdversarialTriageAnalyzer,
    write_report,
)


def test_v122a_cpo_xyz_1min_family_three_run_adversarial_triage(tmp_path: Path) -> None:
    analyzer = V122ACpoXyz1MinFamilyThreeRunAdversarialTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122a_cpo_xyz_1min_family_three_run_adversarial_triage_v1",
        result=result,
    )
    assert result.summary["supportive_continuation_status"] == "candidate_family_only"
    assert result.summary["burst_fade_trap_status"] == "candidate_family_only"
    with output_path.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "run_short_horizon_label_aligned_expectancy_audit"
