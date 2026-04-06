from pathlib import Path

from a_share_quant.strategy.v134hs_commercial_aerospace_training_target_route_audit_v1 import (
    V134HSCommercialAerospaceTrainingTargetRouteAuditV1Analyzer,
)


def test_v134hs_training_route_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HSCommercialAerospaceTrainingTargetRouteAuditV1Analyzer(repo_root).analyze()

    assert report.summary["roadmap_phase_count"] == 5
    assert report.summary["agent_consensus_count"] == 3
    assert report.summary["negative_module_member_count"] == 3
    assert report.summary["decisive_event_retained_count"] >= 1
    assert len(report.phase_rows) == 5
    assert report.phase_rows[0]["phase_name"] == "negative_environment_semantics"
    assert report.phase_rows[1]["phase_name"] == "event_attention_layer"
    assert any(row["label_name"] == "attention_decoy" for row in report.label_rows)
    assert any(row["label_name"] == "capital_true_selection" for row in report.label_rows)
    assert any(row["blocker_name"] == "shadow_boundary_frozen" for row in report.blocker_rows)
    assert any(row["agent_name"] == "Tesla" for row in report.agent_rows)
