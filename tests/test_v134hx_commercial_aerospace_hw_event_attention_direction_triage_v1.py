from pathlib import Path

from a_share_quant.strategy.v134hx_commercial_aerospace_hw_event_attention_direction_triage_v1 import (
    V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Analyzer,
)


def test_v134hx_event_attention_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HXCommercialAerospaceHWEventAttentionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["registry_row_count"] == 8
    directions = {row["supervision_label"]: row["direction"] for row in report.triage_rows}
    assert directions["event_trigger_validity"] == "retain_as_first_event_layer_and_keep_validity_categories_conservative"
    assert directions["attention_anchor"] == "retain_as_role_label_not_as_board_restart_evidence"
    assert directions["capital_true_selection"].startswith("keep_deferred")
