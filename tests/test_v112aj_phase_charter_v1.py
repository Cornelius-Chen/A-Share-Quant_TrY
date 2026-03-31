from pathlib import Path

from a_share_quant.strategy.v112aj_phase_charter_v1 import (
    V112AJPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112aj_phase_charter_opens_dataset_assembly() -> None:
    analyzer = V112AJPhaseCharterAnalyzer()
    result = analyzer.analyze(
        owner_review_payload=load_json_report(Path("reports/analysis/v112ai_cpo_label_draft_integrity_owner_review_v1.json")),
    )
    assert result.summary["do_open_v112aj_now"] is True
