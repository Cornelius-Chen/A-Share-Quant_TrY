from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision_v1 import (
    V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionAnalyzer,
)


def test_v114s_cpo_intraday_state_audit_and_action_outcome_labeling_revision() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114SCpoIntradayStateAuditAndActionOutcomeLabelingRevisionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    assert result.summary["protocol_upgrade"] == (
        "intraday_confirmation_protocol_to_intraday_state_audit_and_action_outcome_labeling_protocol"
    )
    assert result.summary["board_state_layer_count"] >= 5
    assert any(row["field_group"] == "float_and_turnover_rate" for row in result.must_have_rows)
    assert any(row["field_group"] == "tradability_and_session_state" for row in result.must_have_rows)
    assert any(row["action_name"] == "add" for row in result.action_outcome_label_rows)
    assert any(row["gap_name"] == "action_outcome_labels_not_defined_in_data_pipeline" for row in result.current_gap_rows)
