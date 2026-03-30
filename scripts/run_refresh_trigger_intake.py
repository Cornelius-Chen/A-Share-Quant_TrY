from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.refresh_trigger_intake import (
    ALLOWED_REFRESH_TRIGGER_TYPES,
    RefreshTriggerIntakeBuilder,
    write_refresh_trigger_intake,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Persist a newly observed refresh-trigger signal before rerunning the guard stack."
    )
    parser.add_argument("--trigger-name", required=True, help="Short name for the newly observed signal.")
    parser.add_argument(
        "--trigger-type",
        required=True,
        choices=ALLOWED_REFRESH_TRIGGER_TYPES,
        help="Canonical trigger type.",
    )
    parser.add_argument("--source", required=True, help="Where the signal came from.")
    parser.add_argument("--rationale", required=True, help="Why this signal may matter.")
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        help="Affected dataset. Repeat for multiple datasets.",
    )
    parser.add_argument(
        "--symbol",
        action="append",
        default=[],
        help="Affected symbol. Repeat for multiple symbols.",
    )
    parser.add_argument(
        "--slice",
        action="append",
        default=[],
        help="Affected slice. Repeat for multiple slices.",
    )
    parser.add_argument(
        "--report-name",
        default="refresh_trigger_intake_v1",
        help="Output report basename.",
    )
    parser.add_argument(
        "--reports-dir",
        default="reports/analysis",
        help="Directory where the intake report should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    record = RefreshTriggerIntakeBuilder().build(
        trigger_name=args.trigger_name,
        trigger_type=args.trigger_type,
        source=args.source,
        rationale=args.rationale,
        datasets=list(args.dataset),
        symbols=list(args.symbol),
        slices=list(args.slice),
    )
    output_path = write_refresh_trigger_intake(
        reports_dir=Path(args.reports_dir),
        report_name=args.report_name,
        record=record,
    )
    print(f"Refresh trigger intake: {output_path}")
    print(f"Summary: {record.summary}")


if __name__ == "__main__":
    main()
