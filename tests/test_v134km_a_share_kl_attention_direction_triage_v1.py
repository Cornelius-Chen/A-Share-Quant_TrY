from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134km_a_share_kl_attention_direction_triage_v1 import (
    V134KMAShareKLAttentionDirectionTriageV1Analyzer,
)


def test_v134km_attention_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KMAShareKLAttentionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["attention_registry_count"] == 5
    assert report.summary["hard_attention_role_count"] == 1
    assert (
        report.summary["authoritative_status"]
        == "attention_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_label_registry_population"
    )


def test_v134km_attention_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KMAShareKLAttentionDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["attention_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_into_labels_layer_using_attention_registry_as_semantic_input"
