from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.feature_factor_registry_v1 import (
    FeatureFactorRegistryAnalyzer,
)


def test_feature_factor_registry_v1_counts_buckets(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.json"
    evidence.write_text("{}", encoding="utf-8")
    result = FeatureFactorRegistryAnalyzer().analyze(
        root_dir=tmp_path,
        entries=[
            {
                "entry_name": "retained_one",
                "bucket": "retained_feature",
                "source_type": "cycle_family",
                "posture": "retain",
                "rationale": "good",
                "evidence_paths": ["evidence.json"],
            },
            {
                "entry_name": "explainer_one",
                "bucket": "explanatory_only_feature",
                "source_type": "context_branch",
                "posture": "explain",
                "rationale": "good",
                "evidence_paths": ["evidence.json"],
            },
            {
                "entry_name": "candidate_one",
                "bucket": "candidate_factor",
                "source_type": "cycle_family",
                "posture": "candidate",
                "rationale": "good",
                "evidence_paths": ["evidence.json"],
            },
        ],
    )

    assert result.summary["registry_entry_count"] == 3
    assert result.summary["retained_feature_count"] == 1
    assert result.summary["explanatory_only_feature_count"] == 1
    assert result.summary["candidate_factor_count"] == 1
    assert result.summary["ready_for_factor_evaluation_protocol"] is True
