import json
from pathlib import Path

from a_share_quant.strategy.v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1 import (
    V116SCpoExpandedWindowIntradayCandidateCoverageAuditAnalyzer,
)


def test_v116s_expanded_window_intraday_candidate_coverage_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116SCpoExpandedWindowIntradayCandidateCoverageAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
    )
    assert result.summary["acceptance_posture"] == "freeze_v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1"
    assert result.summary["expanded_window_day_count"] >= result.summary["days_with_add_candidate_rows"]
