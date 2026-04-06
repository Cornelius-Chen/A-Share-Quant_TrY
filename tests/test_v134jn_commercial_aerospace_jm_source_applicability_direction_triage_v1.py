from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jn_commercial_aerospace_jm_source_applicability_direction_triage_v1 import (
    V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Analyzer,
)


def test_v134jn_source_applicability_triage_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["same_plane_ready_source_count"] == 1
    assert report.summary["structural_prior_only_source_count"] == 2
    assert (
        report.summary["authoritative_status"]
        == "treat_decisive_event_registry_as_the_first_same_plane_broader_attention_source_and_keep_snapshots_as_structural_priors_only"
    )


def test_v134jn_source_applicability_triage_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JNCommercialAerospaceJMSourceApplicabilityDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["decisive_event_registry_v1"] == "promote_as_first_same_plane_broader_attention_expansion_surface"
    assert directions["market_snapshot_inventory_v6"] == "retain_as_structural_prior_do_not_treat_as_2026_same_plane_evidence"
    assert directions["theme_snapshot_inventory_v7"] == "retain_as_structural_prior_do_not_treat_as_2026_same_plane_evidence"
    assert directions["capital_true_selection"] == "continue_blocked_while_same_plane_broader_attention_evidence_remains_thin"
