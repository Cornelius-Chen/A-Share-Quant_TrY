from pathlib import Path
import json

from a_share_quant.strategy.v121r_cpo_reduce_context_separation_time_split_validation_v1 import (
    V121RCpoReduceContextSeparationTimeSplitValidationAnalyzer,
)


def test_v121r_reduce_context_separation_time_split_validation_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121RCpoReduceContextSeparationTimeSplitValidationAnalyzer(repo_root=repo_root)
    payload = json.loads((repo_root / "reports" / "analysis" / "v121q_cpo_reduce_context_separation_external_audit_v1.json").read_text(encoding="utf-8"))
    result = analyzer.analyze(v121q_payload=payload)
    assert result.summary["split_count"] == 3
    assert result.summary["mean_test_balanced_accuracy"] >= 0.0
