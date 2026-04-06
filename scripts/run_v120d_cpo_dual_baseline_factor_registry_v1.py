from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.v120d_cpo_dual_baseline_factor_registry_v1 import (
    CpoDualBaselineFactorRegistryAnalyzer,
    load_required_payloads,
    write_cpo_dual_baseline_factor_registry_csv,
    write_cpo_dual_baseline_factor_registry_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze authoritative baseline vs research test baseline factor membership for CPO."
    )
    parser.add_argument(
        "--reports-dir",
        default="reports/analysis",
        help="Directory for the output report.",
    )
    parser.add_argument(
        "--report-name",
        default="v120d_cpo_dual_baseline_factor_registry_v1",
        help="Output report stem.",
    )
    parser.add_argument(
        "--csv-output",
        default="data/training/cpo_dual_baseline_factor_registry_v1.csv",
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payloads = load_required_payloads(ROOT)
    result = CpoDualBaselineFactorRegistryAnalyzer().analyze(**payloads)
    report_path = write_cpo_dual_baseline_factor_registry_report(
        reports_dir=Path(args.reports_dir),
        report_name=args.report_name,
        result=result,
    )
    csv_path = write_cpo_dual_baseline_factor_registry_csv(
        output_path=Path(args.csv_output),
        rows=result.baseline_rows,
    )
    print(f"CPO dual baseline factor registry report: {report_path}")
    print(f"CPO dual baseline factor registry csv: {csv_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
