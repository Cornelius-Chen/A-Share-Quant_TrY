from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import load_json_report
from a_share_quant.strategy.v120f_cpo_research_test_baseline_explainer_plots_v1 import (
    CpoResearchTestBaselineExplainerPlotsAnalyzer,
)


def test_research_test_baseline_explainer_plots_generate_assets() -> None:
    repo_root = Path(".").resolve()
    analyzer = CpoResearchTestBaselineExplainerPlotsAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=load_json_report(repo_root / "reports/analysis/v113t_cpo_execution_main_feed_build_v1.json"),
        v114t_payload=load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        v120e_payload=load_json_report(repo_root / "reports/analysis/v120e_cpo_research_test_baseline_overlay_replay_v1.json"),
    )
    assert result.summary["explainer_row_count"] > 0
    assert result.summary["research_test_final_equity"] >= result.summary["baseline_final_equity"]
