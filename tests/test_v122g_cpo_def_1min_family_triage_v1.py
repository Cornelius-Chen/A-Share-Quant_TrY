from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v122g_cpo_def_1min_family_triage_v1 import (
    V122GCpoDef1MinFamilyTriageAnalyzer,
    write_report,
)


def test_v122g_cpo_def_1min_family_triage(tmp_path: Path) -> None:
    analyzer = V122GCpoDef1MinFamilyTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122g_cpo_def_1min_family_triage_v1",
        result=result,
    )
    assert result.summary["burst_fade_trap_status"] == "dead"
    assert result.summary["supportive_continuation_quality_score_status"] == "explanatory_only"
    with output_path.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "build_stricter_1min_action_timepoint_label_base"
