from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.v120e_cpo_research_test_baseline_overlay_replay_v1 import (
    CpoResearchTestBaselineOverlayReplayAnalyzer,
    write_cpo_research_test_baseline_overlay_csv,
    write_cpo_research_test_baseline_overlay_replay_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a research-only CPO test baseline overlay replay using all retained non-dead branches."
    )
    parser.add_argument(
        "--reports-dir",
        default="reports/analysis",
        help="Directory for the output report.",
    )
    parser.add_argument(
        "--report-name",
        default="v120e_cpo_research_test_baseline_overlay_replay_v1",
        help="Output report stem.",
    )
    parser.add_argument(
        "--csv-output",
        default="data/training/cpo_research_test_baseline_overlay_orders_v1.csv",
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = CpoResearchTestBaselineOverlayReplayAnalyzer().analyze()
    report_path = write_cpo_research_test_baseline_overlay_replay_report(
        reports_dir=Path(args.reports_dir),
        report_name=args.report_name,
        result=result,
    )
    csv_path = write_cpo_research_test_baseline_overlay_csv(
        output_path=Path(args.csv_output),
        rows=result.executed_overlay_rows,
    )
    print(f"CPO research test baseline overlay replay report: {report_path}")
    print(f"CPO research test baseline overlay replay csv: {csv_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
