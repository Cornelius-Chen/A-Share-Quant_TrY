from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import load_json_report
from a_share_quant.strategy.v120f_cpo_research_test_baseline_explainer_plots_v1 import (
    CpoResearchTestBaselineExplainerPlotsAnalyzer,
    write_cpo_research_test_baseline_explainer_plots_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create explainer table and plots for the CPO research test baseline replay."
    )
    parser.add_argument(
        "--reports-dir",
        default="reports/analysis",
        help="Directory for the output report.",
    )
    parser.add_argument(
        "--report-name",
        default="v120f_cpo_research_test_baseline_explainer_plots_v1",
        help="Output report stem.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analyzer = CpoResearchTestBaselineExplainerPlotsAnalyzer(repo_root=ROOT)
    result = analyzer.analyze(
        v113t_payload=load_json_report(ROOT / "reports/analysis/v113t_cpo_execution_main_feed_build_v1.json"),
        v114t_payload=load_json_report(ROOT / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        v120e_payload=load_json_report(ROOT / "reports/analysis/v120e_cpo_research_test_baseline_overlay_replay_v1.json"),
    )
    output_path = write_cpo_research_test_baseline_explainer_plots_report(
        reports_dir=Path(args.reports_dir),
        report_name=args.report_name,
        result=result,
    )
    print(f"CPO research test baseline explainer/plots report: {output_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
