from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import (
    CpoCatalystEventRegistryBootstrapAnalyzer,
    load_json_report,
    write_cpo_catalyst_event_registry_bootstrap_report,
    write_cpo_catalyst_event_registry_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap a bounded CPO catalyst/event registry with timestamp resolution where possible."
    )
    parser.add_argument(
        "--information-registry-report",
        default="reports/analysis/v112p_cpo_full_cycle_information_registry_v1.json",
        help="Path to the bounded CPO information registry report.",
    )
    parser.add_argument(
        "--future-calendar-report",
        default="reports/analysis/v112w_cpo_future_catalyst_calendar_operationalization_v1.json",
        help="Path to the CPO future catalyst calendar report.",
    )
    parser.add_argument(
        "--reports-dir",
        default="reports/analysis",
        help="Directory for the output report.",
    )
    parser.add_argument(
        "--report-name",
        default="v120c_cpo_catalyst_event_registry_bootstrap_v1",
        help="Output report stem.",
    )
    parser.add_argument(
        "--csv-output",
        default="data/reference/catalyst_registry/cpo_catalyst_event_registry_v1.csv",
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    information_registry_payload = load_json_report(Path(args.information_registry_report))
    future_calendar_payload = load_json_report(Path(args.future_calendar_report))
    result = CpoCatalystEventRegistryBootstrapAnalyzer().analyze(
        information_registry_payload=information_registry_payload,
        future_calendar_payload=future_calendar_payload,
    )
    report_path = write_cpo_catalyst_event_registry_bootstrap_report(
        reports_dir=Path(args.reports_dir),
        report_name=args.report_name,
        result=result,
    )
    csv_path = write_cpo_catalyst_event_registry_csv(
        output_path=Path(args.csv_output),
        rows=result.registry_rows,
    )
    print(f"CPO catalyst event registry bootstrap report: {report_path}")
    print(f"CPO catalyst event registry bootstrap csv: {csv_path}")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
