import json
from pathlib import Path

from a_share_quant.strategy.v116v_cpo_expanded_window_candidate_coverage_reaudit_v1 import (
    V116VCpoExpandedWindowCandidateCoverageReauditAnalyzer,
)


def test_v116v_expanded_window_candidate_coverage_reaudit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116VCpoExpandedWindowCandidateCoverageReauditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        merged_pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
    )
    assert result.summary["acceptance_posture"] == "freeze_v116v_cpo_expanded_window_candidate_coverage_reaudit_v1"
    assert result.summary["true_coverage_gap_day_count_after_rebuild"] == 0
