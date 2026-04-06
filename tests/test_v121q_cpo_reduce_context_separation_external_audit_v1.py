from pathlib import Path
import json

from a_share_quant.strategy.v121q_cpo_reduce_context_separation_external_audit_v1 import (
    V121QCpoReduceContextSeparationExternalAuditAnalyzer,
)


def test_v121q_reduce_context_separation_external_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121QCpoReduceContextSeparationExternalAuditAnalyzer(repo_root=repo_root)
    payload = json.loads((repo_root / "reports" / "analysis" / "v121p_cpo_reduce_context_separation_discovery_v1.json").read_text(encoding="utf-8"))
    result = analyzer.analyze(v121p_payload=payload)
    assert result.summary["best_balanced_accuracy"] >= 0.0
    assert len(result.threshold_audit_rows) > 0
