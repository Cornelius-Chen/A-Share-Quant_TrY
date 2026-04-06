from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kb_a_share_ka_storage_lifecycle_direction_triage_v1 import (
    V134KBAShareKAStorageLifecycleDirectionTriageV1Analyzer,
)


def test_v134kb_storage_lifecycle_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KBAShareKAStorageLifecycleDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["lifecycle_class_count"] == 10
    assert report.summary["disposable_class_count"] == 3
    assert (
        report.summary["authoritative_status"]
        == "treat_storage_exit_as_first_class_and_keep_only_truth_layers_long_lived_while_defaulting_intermediates_to_ttl_or_archive"
    )


def test_v134kb_storage_lifecycle_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KBAShareKAStorageLifecycleDirectionTriageV1Analyzer(repo_root).analyze()
    directions = [row["direction"] for row in report.triage_rows]

    assert "default_temporary_feature_views_and_candidate_search_outputs_to_ttl_backed_disposable_assets" in directions
