from pathlib import Path

from a_share_quant.strategy.v134ht_commercial_aerospace_hs_route_direction_triage_v1 import (
    V134HTCommercialAerospaceHSRouteDirectionTriageV1Analyzer,
)


def test_v134ht_route_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HTCommercialAerospaceHSRouteDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["roadmap_phase_count"] == 5
    assert report.summary["agent_consensus_count"] == 3
    directions = {row["target_area"]: row["direction"] for row in report.triage_rows}
    assert directions["negative_environment_semantics"] == "promote_as_next_main_supervision_target"
    assert directions["event_attention_layer"] == "promote_immediately_after_negative_environment_semantics"
    assert directions["execution_authority"] == "keep_blocked_do_not_pretend_current_route_is_execution_ready"
