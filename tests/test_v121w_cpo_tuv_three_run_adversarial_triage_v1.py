from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v121w_cpo_tuv_three_run_adversarial_triage_v1 import (
    V121WCpoTuvThreeRunAdversarialTriageAnalyzer,
    write_report,
)


def test_v121w_cpo_tuv_three_run_adversarial_triage(tmp_path: Path) -> None:
    analyzer = V121WCpoTuvThreeRunAdversarialTriageAnalyzer()
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v121w_cpo_tuv_three_run_adversarial_triage_v1",
        result=result,
    )

    assert result.summary["reviewer_consensus"] == "unanimous"
    assert result.summary["forbidden_next_step"] == "any_replay_promotion_or_shadow_replay"

    with output_path.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "1min_microstructure_discovery_on_feature_table"
