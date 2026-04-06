import json
from pathlib import Path

from a_share_quant.strategy.v116q_cpo_expanded_repaired_window_manifest_v1 import (
    V116QCpoExpandedRepairedWindowManifestAnalyzer,
)


def test_v116q_expanded_repaired_window_manifest_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116QCpoExpandedRepairedWindowManifestAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114h_payload=json.loads((repo_root / "reports" / "analysis" / "v114h_cpo_promoted_sizing_behavior_audit_v1.json").read_text(encoding="utf-8")),
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
    )
    assert result.summary["acceptance_posture"] == "freeze_v116q_cpo_expanded_repaired_window_manifest_v1"
    assert result.summary["expanded_repaired_window_day_count"] >= result.summary["original_top_miss_day_count"]
